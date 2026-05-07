"""SDK inventory extraction and inventory-vs-Postman comparison helpers."""

from __future__ import annotations

import json
import re
from typing import Any

from .http_capture import RecordingStubHttpClient
from .invocation import build_module_registry, execute_plan, serialize_plan_args
from .models import InvocationPlan, PostmanEndpoint, SdkEndpointRecord
from .paths import CATALOG_DIR
from .postman import find_postman_match

PATH_PARAMETER_ALIASES = {
    "md": "mahadasha",
    "planetname": "planet",
    "zodiacname": "zodiac",
}


def normalize_sdk_endpoint(endpoint: str, path_values: dict[str, Any]) -> str:
    """Normalize an SDK endpoint by replacing concrete path values with placeholders."""
    normalized_parts: list[str] = []
    stringified = {name: str(value) for name, value in path_values.items()}
    for part in endpoint.split("/"):
        matched_name = next(
            (name for name, value in stringified.items() if value == part),
            None,
        )
        if matched_name:
            normalized_parts.append(f"<{matched_name}>")
        else:
            normalized_parts.append(part)
    return "/".join(normalized_parts)


def build_sdk_inventory(
    plans: list[InvocationPlan],
    postman_entries: list[PostmanEndpoint],
    api_key: str = "ak-test-key",
) -> list[SdkEndpointRecord]:
    """Extract a machine-readable SDK inventory using the same invocation plans as live QA."""
    stub = RecordingStubHttpClient(api_key=api_key)
    registry = build_module_registry(stub)
    records: list[SdkEndpointRecord] = []

    for plan in plans:
        stub.reset()
        execute_plan(plan, registry)
        capture = stub.last_capture
        if capture is None:
            raise RuntimeError(f"No capture recorded for {plan.target}")

        capture.target = plan.target
        capture.path_values = {
            key: str(value)
            for key, value in plan.path_values.items()
        }
        capture.invocation_args = serialize_plan_args(plan)
        capture.normalized_endpoint = normalize_sdk_endpoint(
            capture.endpoint,
            plan.path_values,
        )

        matched_postman = find_postman_match(postman_entries, capture)
        records.append(
            SdkEndpointRecord(
                module_name=plan.module_name,
                method_name=plan.method_name,
                target=plan.target,
                endpoint=capture.endpoint,
                normalized_endpoint=capture.normalized_endpoint,
                domain=capture.domain,
                request_encoding=capture.body_mode,
                request_fields=sorted(capture.body.keys()),
                path_parameters=list(plan.path_values.keys()),
                example_request_body=capture.body,
                auth_style=capture.auth_style,
                matched_postman_endpoint=(
                    matched_postman.endpoint if matched_postman else None
                ),
                matched_postman_normalized_endpoint=(
                    matched_postman.normalized_endpoint if matched_postman else None
                ),
            )
        )

    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    output_path = CATALOG_DIR / "sdk-endpoints.json"
    output_path.write_text(
        json.dumps([record.to_dict() for record in records], indent=2) + "\n"
    )
    return records


def _clean_path_name(name: str) -> str:
    cleaned = name.lstrip(":")
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", cleaned)
    lowered = cleaned.lower()
    return PATH_PARAMETER_ALIASES.get(lowered, lowered)


def compare_inventories(
    sdk_records: list[SdkEndpointRecord],
    postman_entries: list[PostmanEndpoint],
) -> tuple[list[PostmanEndpoint], list[SdkEndpointRecord], list[dict[str, Any]]]:
    """Compare SDK and Postman inventories for coverage and parameter mismatches."""
    sdk_normalized = {record.normalized_endpoint for record in sdk_records}
    postman_normalized = {entry.normalized_endpoint for entry in postman_entries}

    missing_in_sdk = [
        entry
        for entry in postman_entries
        if entry.normalized_endpoint not in sdk_normalized
    ]
    missing_in_postman = [
        record
        for record in sdk_records
        if record.normalized_endpoint not in postman_normalized
    ]

    parameter_mismatches: list[dict[str, Any]] = []
    postman_by_normalized = {
        entry.normalized_endpoint: entry
        for entry in postman_entries
    }
    for record in sdk_records:
        matched_key = record.matched_postman_normalized_endpoint
        if not matched_key:
            continue

        postman_entry = postman_by_normalized[matched_key]
        postman_fields = sorted(
            parameter["key"]
            for parameter in postman_entry.body_parameters
            if not parameter.get("disabled")
        )
        missing_sdk_fields = sorted(set(postman_fields) - set(record.request_fields))
        extra_sdk_fields = sorted(set(record.request_fields) - set(postman_fields))

        postman_path_parameters = [
            _clean_path_name(name)
            for name in postman_entry.path_parameters
        ]
        sdk_path_parameters = [
            _clean_path_name(name)
            for name in record.path_parameters
        ]

        if (
            missing_sdk_fields
            or extra_sdk_fields
            or postman_path_parameters != sdk_path_parameters
            or record.request_encoding != (
                "form" if postman_entry.body_mode == "urlencoded" else "json"
            )
        ):
            parameter_mismatches.append(
                {
                    "target": record.target,
                    "sdkEndpoint": record.endpoint,
                    "sdkNormalizedEndpoint": record.normalized_endpoint,
                    "postmanEndpoint": postman_entry.endpoint,
                    "postmanNormalizedEndpoint": postman_entry.normalized_endpoint,
                    "sdkFields": record.request_fields,
                    "postmanFields": postman_fields,
                    "missingSdkFields": missing_sdk_fields,
                    "extraSdkFields": extra_sdk_fields,
                    "sdkPathParameters": sdk_path_parameters,
                    "postmanPathParameters": postman_path_parameters,
                    "sdkRequestEncoding": record.request_encoding,
                    "postmanRequestEncoding": (
                        "form" if postman_entry.body_mode == "urlencoded" else "json"
                    ),
                }
            )

    return missing_in_sdk, missing_in_postman, parameter_mismatches
