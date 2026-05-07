"""
Internal HTTP client for AstrologyAPI.

Handles:
- inferred header or Basic authentication
- Base URL selection (JSON vs PDF)
- Error mapping to typed SDK exceptions
- Retry logic with exponential backoff
- Both sync and async clients
"""

from __future__ import annotations

import asyncio
import base64
import os
import time
from typing import Any, TypeVar

import httpx

from .errors import (
    AstrologyAPIError,
    AuthenticationError,
    NetworkError,
    NotFoundError,
    PlanRestrictedError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ValidationError,
)

T = TypeVar("T")

BASE_JSON_URL = "https://json.astrologyapi.com/v1"
BASE_PDF_URL = "https://pdf.astrologyapi.com/v1"
USER_AGENT = "astrologyapi-python/2.0.0"


def _extract_message(data: Any) -> str | None:
    """Extract error message from API response."""
    if isinstance(data, dict):
        if "message" in data:
            return data["message"]
        if "error" in data:
            return data["error"]
    return None


def _map_error(status_code: int, message: str, data: Any) -> AstrologyAPIError:
    """Map HTTP status code and response to typed error."""
    if status_code in (400, 422):
        return ValidationError(message, status_code, data)
    if status_code == 401:
        return AuthenticationError(
            "Authentication failed. Check your AstrologyAPI credentials.",
            status_code,
            data,
        )
    if status_code == 402:
        return QuotaExceededError(
            "API quota exceeded. Please upgrade your plan at astrologyapi.com.",
            data,
        )
    if status_code == 403:
        return PlanRestrictedError(
            "This endpoint is not available on your current plan.",
            data,
        )
    if status_code == 404:
        return NotFoundError(message, data)
    if status_code == 429:
        return RateLimitError(message, None, data)
    if 500 <= status_code < 600:
        return ServerError(message, status_code, data)
    return AstrologyAPIError(message, status_code, data)


def infer_auth_style(api_key: str) -> str:
    """Infer auth style from the configured credential string."""
    return "header" if "ak-" in api_key else "basic"


def _build_basic_credential(api_key: str) -> str:
    """
    Build the Basic auth credential payload.

    The shared QA docs model legacy auth as `userId:apiKey`. If the configured
    value already contains `:`, use it as-is; otherwise fall back to
    `ASTROLOGYAPI_USER_ID` when present.
    """
    if ":" in api_key:
        return api_key

    user_id = os.getenv("ASTROLOGYAPI_USER_ID")
    if user_id:
        return f"{user_id}:{api_key}"

    return api_key


def build_auth_headers(api_key: str) -> tuple[str, dict[str, str]]:
    """Build auth headers using the shared cross-SDK inference rule."""
    auth_style = infer_auth_style(api_key)
    if auth_style == "header":
        return auth_style, {"x-astrologyapi-key": api_key}

    encoded = base64.b64encode(
        _build_basic_credential(api_key).encode("utf-8")
    ).decode("ascii")
    return auth_style, {"Authorization": f"Basic {encoded}"}


def build_headers(api_key: str, body_mode: str = "json") -> tuple[str, dict[str, str]]:
    """Build request headers for runtime and QA direct calls."""
    auth_style, headers = build_auth_headers(api_key)
    headers["Content-Type"] = (
        "application/x-www-form-urlencoded"
        if body_mode == "form"
        else "application/json"
    )
    headers["User-Agent"] = USER_AGENT
    return auth_style, headers


def build_request_kwargs(
    body: dict[str, Any] | None,
    body_mode: str = "json",
) -> dict[str, Any]:
    """Build httpx request kwargs without mutating scalar values."""
    if body is None:
        body = {}

    filtered = {
        key: value
        for key, value in body.items()
        if value is not None
    }
    if body_mode == "form":
        return {"data": filtered}
    return {"json": filtered}


def _parse_success_response(response: httpx.Response, domain: str) -> Any:
    """Parse successful responses, including PDF endpoints that return JSON."""
    content_type = response.headers.get("content-type", "").lower()

    if domain == "pdf":
        if "json" in content_type:
            try:
                return response.json()
            except Exception:
                return response.text

        if "pdf" in content_type or response.content.startswith(b"%PDF"):
            return response.content

        try:
            return response.json()
        except Exception:
            return response.content

    try:
        return response.json()
    except Exception:
        return response.text


def _parse_error_payload(response: httpx.Response) -> Any:
    """Parse error payloads without assuming JSON."""
    try:
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return response.text
    except Exception:
        return None


class HttpClient:
    """
    Synchronous HTTP client for AstrologyAPI.

    Handles authentication, error mapping, and retry logic.
    """

    def __init__(
        self,
        api_key: str,
        timeout: float = 30.0,
        retries: int = 3,
    ) -> None:
        """
        Initialize the sync HTTP client.

        Args:
            api_key: AstrologyAPI API key or legacy combined credential string
            timeout: Request timeout in seconds
            retries: Number of retry attempts for transient errors
        """
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self.client = httpx.Client(timeout=timeout)

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying httpx client."""
        self.client.close()

    def build_headers(self, body_mode: str = "json") -> tuple[str, dict[str, str]]:
        """Build request headers using the configured credential."""
        return build_headers(self.api_key, body_mode)

    def build_request_kwargs(
        self,
        body: dict[str, Any] | None,
        body_mode: str = "json",
    ) -> dict[str, Any]:
        """Build outbound httpx request kwargs."""
        return build_request_kwargs(body, body_mode)

    def post(
        self,
        endpoint: str,
        body: dict[str, Any] | None = None,
        domain: str = "json",
        body_mode: str = "json",
    ) -> Any:
        """
        Make a POST request to the API.

        Args:
            endpoint: API endpoint (without domain/version prefix)
            body: Request body as dictionary
            domain: "json" or "pdf"
            body_mode: "json" or "form"

        Returns:
            Parsed response data (dict/text for JSON, bytes or dict for PDF)

        Raises:
            Various AstrologyAPIError subclasses
        """
        base_url = BASE_PDF_URL if domain == "pdf" else BASE_JSON_URL
        url = f"{base_url}/{endpoint}"
        _, headers = self.build_headers(body_mode)
        request_kwargs = self.build_request_kwargs(body, body_mode)

        attempt = 0
        while attempt <= self.retries:
            try:
                response = self.client.post(url, headers=headers, **request_kwargs)

                if response.status_code < 400:
                    return _parse_success_response(response, domain)

                data = _parse_error_payload(response)
                message = (
                    _extract_message(data)
                    or response.reason_phrase
                    or "Unknown error"
                )

                if response.status_code == 429:
                    retry_after = None
                    retry_after_header = response.headers.get("Retry-After")
                    if retry_after_header:
                        try:
                            retry_after = int(retry_after_header)
                        except ValueError:
                            pass
                    raise RateLimitError(message, retry_after, data)

                raise _map_error(response.status_code, message, data)

            except (httpx.RequestError, httpx.TimeoutException) as exc:
                if attempt >= self.retries:
                    raise NetworkError(
                        f"Network request failed after {self.retries + 1} attempts",
                        exc,
                    )
                attempt += 1
                time.sleep(2 ** (attempt - 1))
                continue

            except AstrologyAPIError:
                raise

    def post_binary(
        self,
        endpoint: str,
        body: dict[str, Any] | None = None,
        body_mode: str = "form",
    ) -> Any:
        """
        Make a POST request expecting a PDF-style response.

        PDF endpoints may return either binary PDF bytes or a successful JSON
        report payload containing `pdf_url`.
        """
        return self.post(endpoint, body, domain="pdf", body_mode=body_mode)


class AsyncHttpClient:
    """
    Asynchronous HTTP client for AstrologyAPI.

    Provides the same interface as HttpClient but with async/await.
    """

    def __init__(
        self,
        api_key: str,
        timeout: float = 30.0,
        retries: int = 3,
    ) -> None:
        """
        Initialize the async HTTP client.

        Args:
            api_key: AstrologyAPI API key or legacy combined credential string
            timeout: Request timeout in seconds
            retries: Number of retry attempts for transient errors
        """
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self.client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> "AsyncHttpClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying httpx async client."""
        await self.client.aclose()

    async def post_binary(
        self,
        endpoint: str,
        body: dict[str, Any] | None = None,
        body_mode: str = "form",
    ) -> Any:
        """
        Make an async POST request expecting a PDF-style response.

        PDF endpoints may return either binary PDF bytes or a successful JSON
        report payload containing `pdf_url`.
        """
        return await self.post(endpoint, body, domain="pdf", body_mode=body_mode)

    async def post(
        self,
        endpoint: str,
        body: dict[str, Any] | None = None,
        domain: str = "json",
        body_mode: str = "json",
    ) -> Any:
        """
        Make an async POST request to the API.

        Args:
            endpoint: API endpoint (without domain/version prefix)
            body: Request body as dictionary
            domain: "json" or "pdf"
            body_mode: "json" or "form"

        Returns:
            Parsed response data (dict/text for JSON, bytes or dict for PDF)

        Raises:
            Various AstrologyAPIError subclasses
        """
        base_url = BASE_PDF_URL if domain == "pdf" else BASE_JSON_URL
        url = f"{base_url}/{endpoint}"
        _, headers = build_headers(self.api_key, body_mode)
        request_kwargs = build_request_kwargs(body, body_mode)

        attempt = 0
        while attempt <= self.retries:
            try:
                response = await self.client.post(
                    url,
                    headers=headers,
                    **request_kwargs,
                )

                if response.status_code < 400:
                    return _parse_success_response(response, domain)

                data = _parse_error_payload(response)
                message = (
                    _extract_message(data)
                    or response.reason_phrase
                    or "Unknown error"
                )

                if response.status_code == 429:
                    retry_after = None
                    retry_after_header = response.headers.get("Retry-After")
                    if retry_after_header:
                        try:
                            retry_after = int(retry_after_header)
                        except ValueError:
                            pass
                    raise RateLimitError(message, retry_after, data)

                raise _map_error(response.status_code, message, data)

            except (httpx.RequestError, httpx.TimeoutException) as exc:
                if attempt >= self.retries:
                    raise NetworkError(
                        f"Network request failed after {self.retries + 1} attempts",
                        exc,
                    )
                attempt += 1
                await asyncio.sleep(2 ** (attempt - 1))
                continue

            except AstrologyAPIError:
                raise
