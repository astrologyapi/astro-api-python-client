"""Postman inventory loading and direct-request reconstruction helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import DirectRequestSpec, PostmanEndpoint, RequestCapture
from .paths import CATALOG_DIR, POSTMAN_DIR

POSTMAN_MATCH_ALIASES = {
    "horoscopes.get_next": "sun_sign_prediction/next/<zodiac>",
    "horoscopes.get_previous": "sun_sign_prediction/previous/<zodiac>",
    "vedic.get_extended_chart": "horo_chart_extended",
}


def load_postman_inventory(write_catalog_copy: bool = True) -> list[PostmanEndpoint]:
    """Load the normalized Postman inventory from the shared testing assets."""
    source = POSTMAN_DIR / "postman-endpoints.json"
    if not source.exists():
        raise FileNotFoundError(
            "Expected normalized Postman inventory at "
            f"{source}. The shared testing assets are incomplete."
        )

    data = json.loads(source.read_text())
    if write_catalog_copy:
        CATALOG_DIR.mkdir(parents=True, exist_ok=True)
        catalog_path = CATALOG_DIR / "postman-endpoints.json"
        catalog_path.write_text(json.dumps(data, indent=2) + "\n")

    return [PostmanEndpoint.from_dict(item) for item in data]


def _template_to_regex(template: str) -> re.Pattern[str]:
    escaped = re.escape(template)
    escaped = re.sub(r":[^/]+", r"[^/]+", escaped)
    return re.compile(rf"^{escaped}$")


def _materialize_endpoint(template: str, capture: RequestCapture) -> str:
    """Materialize a Postman template using the SDK-captured path values."""
    if ":" not in template:
        return template

    values = list(capture.path_values.values())
    parts = template.split("/")
    value_index = 0
    resolved: list[str] = []
    for part in parts:
        if part.startswith(":") and value_index < len(values):
            resolved.append(str(values[value_index]))
            value_index += 1
        else:
            resolved.append(part)

    materialized = "/".join(resolved)
    if ":" in materialized:
        return capture.endpoint
    return materialized


def find_postman_match(
    entries: list[PostmanEndpoint],
    capture: RequestCapture,
) -> PostmanEndpoint | None:
    """Find the best Postman match for an SDK-captured request."""
    for entry in entries:
        if entry.normalized_endpoint == capture.normalized_endpoint:
            return entry

    alias = POSTMAN_MATCH_ALIASES.get(capture.target)
    if alias:
        for entry in entries:
            if entry.normalized_endpoint == alias:
                return entry

    for entry in entries:
        if _template_to_regex(entry.endpoint).match(capture.endpoint):
            return entry

    return None


def find_postman_by_lookup(
    entries: list[PostmanEndpoint],
    lookup: str,
) -> PostmanEndpoint | None:
    """Resolve a manual single-endpoint lookup by normalized endpoint or display name."""
    normalized_lookup = lookup.strip().lower()
    for entry in entries:
        if entry.normalized_endpoint.lower() == normalized_lookup:
            return entry
        if entry.endpoint.lower() == normalized_lookup:
            return entry
        if normalized_lookup in {name.lower() for name in entry.display_names}:
            return entry
    return None


def build_direct_request_from_postman(
    entry: PostmanEndpoint,
    capture: RequestCapture,
) -> DirectRequestSpec:
    """Build a direct API request from Postman while preferring SDK-captured scalars."""
    sdk_body = capture.body or {}
    body: dict[str, Any] = {}
    for parameter in entry.body_parameters:
        if parameter.get("disabled"):
            continue
        key = parameter["key"]
        if key in sdk_body:
            body[key] = sdk_body[key]
        else:
            body[key] = parameter.get("value")

    materialized_endpoint = _materialize_endpoint(entry.endpoint, capture)
    divergence = {
        "missing_sdk_fields": sorted(set(sdk_body) - set(body)),
        "stale_postman_fields": sorted(set(body) - set(sdk_body)),
    }
    if materialized_endpoint != capture.endpoint:
        divergence["endpoint_mismatch"] = [
            f"{materialized_endpoint} != {capture.endpoint}"
        ]

    body_mode = "form" if entry.body_mode == "urlencoded" else "json"
    return DirectRequestSpec(
        endpoint=materialized_endpoint,
        normalized_endpoint=entry.normalized_endpoint,
        domain=entry.domain,
        body_mode=body_mode,
        body=body,
        source="postman",
        divergence=divergence,
        matched_postman_lookup=entry.normalized_endpoint,
    )


def build_direct_request_from_sdk_capture(capture: RequestCapture) -> DirectRequestSpec:
    """Build a fallback direct request that mirrors the SDK-captured request exactly."""
    return DirectRequestSpec(
        endpoint=capture.endpoint,
        normalized_endpoint=capture.normalized_endpoint,
        domain=capture.domain,
        body_mode=capture.body_mode,
        body=capture.body,
        source="sdk-capture",
    )
