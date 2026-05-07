"""
AstrologyAPI error hierarchy.

Provides typed exception classes for all AstrologyAPI errors,
matching the Node.js and PHP SDK error models.
"""

from __future__ import annotations


class AstrologyAPIError(Exception):
    """
    Base error for all AstrologyAPI SDK errors.
    Catch this to handle any SDK-level error in one place.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        data: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.data = data


class AuthenticationError(AstrologyAPIError):
    """
    Thrown when the API key is missing or invalid (HTTP 401/403).
    """

    def __init__(
        self,
        message: str = "Invalid API key.",
        status_code: int | None = None,
        data: dict | None = None,
    ) -> None:
        super().__init__(message, status_code or 401, data)


class QuotaExceededError(AstrologyAPIError):
    """
    Thrown when the API quota or plan limit has been reached (HTTP 402).
    """

    def __init__(
        self,
        message: str = "API quota exceeded. Please upgrade your plan.",
        data: dict | None = None,
    ) -> None:
        super().__init__(message, 402, data)


class PlanRestrictedError(AstrologyAPIError):
    """
    Thrown when an endpoint is not available on the current plan (HTTP 403).
    """

    def __init__(
        self,
        message: str = "This endpoint is not available on your current plan.",
        data: dict | None = None,
    ) -> None:
        super().__init__(message, 403, data)


class NotFoundError(AstrologyAPIError):
    """
    Thrown when a resource is not found (HTTP 404).
    """

    def __init__(
        self,
        message: str = "Resource not found.",
        data: dict | None = None,
    ) -> None:
        super().__init__(message, 404, data)


class ValidationError(AstrologyAPIError):
    """
    Thrown when a request parameter is invalid (HTTP 400/422).
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        data: dict | None = None,
    ) -> None:
        super().__init__(message, status_code or 422, data)


class RateLimitError(AstrologyAPIError):
    """
    Thrown when the API rate limit is exceeded (HTTP 429).
    Includes optional retry_after hint from the API.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please wait before retrying.",
        retry_after: int | None = None,
        data: dict | None = None,
    ) -> None:
        super().__init__(message, 429, data)
        self.retry_after = retry_after


class ServerError(AstrologyAPIError):
    """
    Thrown when the API returns a 5xx server error.
    """

    def __init__(
        self,
        message: str = "AstrologyAPI server error. Please try again later.",
        status_code: int | None = None,
        data: dict | None = None,
    ) -> None:
        super().__init__(message, status_code or 500, data)


class NetworkError(AstrologyAPIError):
    """
    Thrown when the request could not reach the server
    (network error, timeout, etc.).
    """

    def __init__(
        self,
        message: str = "Unable to reach AstrologyAPI. Check your network connection.",
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message, None, None)
        self.cause = cause
