"""Typed models used by the reusable QA framework."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RequestCapture:
    """Redacted request snapshot captured from an SDK or direct API call."""

    endpoint: str
    domain: str
    body_mode: str
    body: dict[str, Any]
    headers: dict[str, str]
    auth_style: str
    target: str = ""
    normalized_endpoint: str = ""
    path_values: dict[str, Any] = field(default_factory=dict)
    invocation_args: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PostmanEndpoint:
    """Normalized Postman inventory entry."""

    normalized_endpoint: str
    endpoint: str
    domain: str
    method: str
    display_names: list[str]
    source_files: list[str]
    body_mode: str
    body_parameters: list[dict[str, Any]]
    path_parameters: list[str]
    auth_styles: list[str]
    header_keys: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PostmanEndpoint":
        return cls(
            normalized_endpoint=data["normalizedEndpoint"],
            endpoint=data["endpoint"],
            domain=data["domain"],
            method=data["method"],
            display_names=data.get("displayNames", []),
            source_files=data.get("sourceFiles", []),
            body_mode=data.get("bodyMode", "urlencoded"),
            body_parameters=data.get("bodyParameters", []),
            path_parameters=data.get("pathParameters", []),
            auth_styles=data.get("authStyles", []),
            header_keys=data.get("headerKeys", []),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "normalizedEndpoint": self.normalized_endpoint,
            "endpoint": self.endpoint,
            "domain": self.domain,
            "method": self.method,
            "displayNames": self.display_names,
            "sourceFiles": self.source_files,
            "bodyMode": self.body_mode,
            "bodyParameters": self.body_parameters,
            "pathParameters": self.path_parameters,
            "authStyles": self.auth_styles,
            "headerKeys": self.header_keys,
        }


@dataclass
class InvocationPlan:
    """One deterministic SDK invocation used by inventory and live QA runners."""

    target: str
    module_name: str
    method_name: str
    args: list[Any]
    kwargs: dict[str, Any]
    path_values: dict[str, Any]
    parameter_names: list[str]


@dataclass
class SdkEndpointRecord:
    """Machine-readable SDK inventory entry."""

    module_name: str
    method_name: str
    target: str
    endpoint: str
    normalized_endpoint: str
    domain: str
    request_encoding: str
    request_fields: list[str]
    path_parameters: list[str]
    example_request_body: dict[str, Any]
    auth_style: str
    matched_postman_endpoint: str | None = None
    matched_postman_normalized_endpoint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SweepResult:
    """Result of one deterministic SDK live execution."""

    status: str
    target: str
    module_name: str
    method_name: str
    endpoint: str
    normalized_endpoint: str
    domain: str
    request: RequestCapture
    response: Any = None
    response_shape: Any = None
    error_name: str | None = None
    error_message: str | None = None
    status_code: int | None = None


@dataclass
class DirectRequestSpec:
    """Prepared direct API request used by comparison and debug runners."""

    endpoint: str
    normalized_endpoint: str
    domain: str
    body_mode: str
    body: dict[str, Any]
    source: str
    divergence: dict[str, list[str]] = field(default_factory=dict)
    matched_postman_lookup: str | None = None


@dataclass
class CompareResult:
    """Result of one SDK-vs-direct comparison."""

    status: str
    target: str
    endpoint: str
    normalized_endpoint: str
    sdk_request: RequestCapture
    direct_request: RequestCapture | None
    sdk_response: Any
    direct_response: Any = None
    diff: list[str] = field(default_factory=list)
    fallback_reason: str | None = None
    error_name: str | None = None
    error_message: str | None = None
    status_code: int | None = None
