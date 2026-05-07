"""Request capture and redaction helpers for QA runners and reports."""

from __future__ import annotations

from typing import Any, Mapping

from .._http import build_headers
from ..models import BirthData, NumeroData, PDFBranding
from .models import RequestCapture


def redact_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Redact secret-bearing headers before any artifact is written to disk."""
    redacted: dict[str, str] = {}
    for key, value in headers.items():
        lowered = key.lower()
        if lowered == "x-astrologyapi-key":
            redacted[key] = "[REDACTED]"
        elif lowered == "authorization":
            redacted[key] = "Basic [REDACTED]"
        else:
            redacted[key] = value
    return redacted


def serialize_value(value: Any) -> Any:
    """Convert SDK values into report-friendly snapshots."""
    if isinstance(value, BirthData):
        return value.to_dict()
    if isinstance(value, NumeroData):
        return value.to_dict()
    if isinstance(value, PDFBranding):
        return value.to_dict()
    if isinstance(value, bytes):
        return {
            "type": "bytes",
            "length": len(value),
            "is_pdf": value.startswith(b"%PDF"),
        }
    if isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize_value(item) for key, item in value.items()}
    return value


class RecordingStubHttpClient:
    """In-memory HTTP stub used to extract SDK inventory without live traffic."""

    def __init__(self, api_key: str = "ak-test-key") -> None:
        self.api_key = api_key
        self.last_capture: RequestCapture | None = None
        self.last_response: Any = None

    def build_headers(self, body_mode: str = "json") -> tuple[str, dict[str, str]]:
        return build_headers(self.api_key, body_mode)

    def reset(self) -> None:
        self.last_capture = None
        self.last_response = None

    def _capture(
        self,
        endpoint: str,
        body: dict[str, Any] | None,
        domain: str,
        body_mode: str,
    ) -> None:
        auth_style, headers = self.build_headers(body_mode)
        self.last_capture = RequestCapture(
            endpoint=endpoint,
            domain=domain,
            body_mode=body_mode,
            body=serialize_value(body or {}),
            headers=redact_headers(headers),
            auth_style=auth_style,
        )

    def post(
        self,
        endpoint: str,
        body: dict[str, Any] | None = None,
        domain: str = "json",
        body_mode: str = "json",
    ) -> Any:
        self._capture(endpoint, body, domain, body_mode)
        if domain == "pdf":
            self.last_response = {"status": True, "pdf_url": "https://example.com/mock.pdf"}
        else:
            self.last_response = {"status": True, "mock": True}
        return self.last_response

    def post_binary(
        self,
        endpoint: str,
        body: dict[str, Any] | None = None,
        body_mode: str = "form",
    ) -> Any:
        return self.post(endpoint, body, domain="pdf", body_mode=body_mode)


class RecordingHttpClient:
    """Delegating HTTP wrapper that records redacted request/response snapshots."""

    def __init__(self, delegate: Any) -> None:
        self.delegate = delegate
        self.api_key = getattr(delegate, "api_key", "")
        self.last_capture: RequestCapture | None = None
        self.last_response: Any = None
        self.last_exception: Exception | None = None

    def reset(self) -> None:
        self.last_capture = None
        self.last_response = None
        self.last_exception = None

    def build_headers(self, body_mode: str = "json") -> tuple[str, dict[str, str]]:
        return self.delegate.build_headers(body_mode)

    def _capture(
        self,
        endpoint: str,
        body: dict[str, Any] | None,
        domain: str,
        body_mode: str,
    ) -> None:
        auth_style, headers = self.build_headers(body_mode)
        self.last_capture = RequestCapture(
            endpoint=endpoint,
            domain=domain,
            body_mode=body_mode,
            body=serialize_value(body or {}),
            headers=redact_headers(headers),
            auth_style=auth_style,
        )

    def post(
        self,
        endpoint: str,
        body: dict[str, Any] | None = None,
        domain: str = "json",
        body_mode: str = "json",
    ) -> Any:
        self.reset()
        self._capture(endpoint, body, domain, body_mode)
        try:
            self.last_response = self.delegate.post(
                endpoint,
                body,
                domain=domain,
                body_mode=body_mode,
            )
            return self.last_response
        except Exception as exc:
            self.last_exception = exc
            raise

    def post_binary(
        self,
        endpoint: str,
        body: dict[str, Any] | None = None,
        body_mode: str = "form",
    ) -> Any:
        self.reset()
        self._capture(endpoint, body, "pdf", body_mode)
        try:
            self.last_response = self.delegate.post_binary(
                endpoint,
                body,
                body_mode=body_mode,
            )
            return self.last_response
        except Exception as exc:
            self.last_exception = exc
            raise

    def close(self) -> None:
        close = getattr(self.delegate, "close", None)
        if callable(close):
            close()
