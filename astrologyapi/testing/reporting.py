"""Markdown report generation for QA inventories and live results."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from .models import CompareResult, PostmanEndpoint, SdkEndpointRecord, SweepResult
from .paths import RESULTS_DIR, CATALOG_DIR


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_block(value: Any) -> str:
    return "```json\n" + json.dumps(value, indent=2, default=str) + "\n```"


def _write(path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n")


def is_compare_payload_mismatch(result: CompareResult) -> bool:
    """Return True only when a compare-mode failure is a real payload mismatch."""
    return (
        result.status == "failure"
        and result.error_name is None
        and result.sdk_response is not None
        and result.direct_response is not None
        and bool(result.diff)
    )


def split_compare_results(
    results: list[CompareResult],
) -> tuple[list[CompareResult], list[CompareResult]]:
    """Separate true payload mismatches from compare execution failures."""
    mismatches = [result for result in results if is_compare_payload_mismatch(result)]
    execution_failures = [
        result
        for result in results
        if result.status == "failure" and not is_compare_payload_mismatch(result)
    ]
    return mismatches, execution_failures


def write_missing_apis_report(
    missing_in_sdk: list[PostmanEndpoint],
    missing_in_postman: list[SdkEndpointRecord],
) -> None:
    lines = [
        "# Missing APIs",
        "",
        f"Generated at: {_now_iso()}",
        "",
        f"- Postman endpoints missing from SDK: `{len(missing_in_sdk)}`",
        f"- SDK endpoints missing from Postman: `{len(missing_in_postman)}`",
        "",
        "## Postman But Missing In SDK",
        "",
    ]
    if missing_in_sdk:
        for entry in missing_in_sdk:
            lines.extend(
                [
                    f"### `{entry.normalized_endpoint}`",
                    f"- Endpoint: `{entry.endpoint}`",
                    f"- Domain: `{entry.domain}`",
                    f"- Body mode: `{entry.body_mode}`",
                    "",
                ]
            )
    else:
        lines.append("None.")
        lines.append("")

    lines.extend(["## SDK But Missing In Postman", ""])
    if missing_in_postman:
        for record in missing_in_postman:
            lines.extend(
                [
                    f"### `{record.target}`",
                    f"- SDK endpoint: `{record.endpoint}`",
                    f"- Normalized endpoint: `{record.normalized_endpoint}`",
                    f"- Domain: `{record.domain}`",
                    "",
                ]
            )
    else:
        lines.append("None.")

    _write(RESULTS_DIR / "missing-apis.md", "\n".join(lines))


def write_parameter_mismatches_report(mismatches: list[dict[str, Any]]) -> None:
    lines = [
        "# Parameter Mismatches",
        "",
        f"Generated at: {_now_iso()}",
        "",
        f"- Mismatched endpoints: `{len(mismatches)}`",
        "",
    ]
    if not mismatches:
        lines.append("None.")
    else:
        for mismatch in mismatches:
            lines.extend(
                [
                    f"## `{mismatch['target']}`",
                    f"- SDK endpoint: `{mismatch['sdkEndpoint']}`",
                    f"- Postman endpoint: `{mismatch['postmanEndpoint']}`",
                    f"- SDK encoding: `{mismatch['sdkRequestEncoding']}`",
                    f"- Postman encoding: `{mismatch['postmanRequestEncoding']}`",
                    f"- Missing SDK fields: `{', '.join(mismatch['missingSdkFields']) or 'none'}`",
                    f"- Extra SDK fields: `{', '.join(mismatch['extraSdkFields']) or 'none'}`",
                    f"- SDK path params: `{', '.join(mismatch['sdkPathParameters']) or 'none'}`",
                    f"- Postman path params: `{', '.join(mismatch['postmanPathParameters']) or 'none'}`",
                    "",
                    _json_block(
                        {
                            "sdkFields": mismatch["sdkFields"],
                            "postmanFields": mismatch["postmanFields"],
                        }
                    ),
                    "",
                ]
            )

    _write(RESULTS_DIR / "parameter-mismatches.md", "\n".join(lines))


def write_failing_apis_report(results: list[SweepResult]) -> None:
    failures = [result for result in results if result.status == "failure"]
    grouped: dict[str, list[SweepResult]] = defaultdict(list)
    for failure in failures:
        signature = (
            f"HTTP {failure.status_code or 'n/a'} | "
            f"{failure.error_name or 'UnknownError'} | "
            f"{failure.error_message or 'Unknown error'}"
        )
        grouped[signature].append(failure)

    lines = [
        "# Failing APIs",
        "",
        f"Generated at: {_now_iso()}",
        "",
        f"- Total failing APIs: `{len(failures)}`",
        f"- Error groups: `{len(grouped)}`",
        "",
        "## Error Summary",
        "",
    ]
    if grouped:
        for signature, group in grouped.items():
            lines.append(f"- `{signature}` -> `{len(group)}`")
    else:
        lines.append("None.")

    for signature, group in grouped.items():
        lines.extend(["", f"## `{signature}`", ""])
        for failure in group:
            lines.extend(
                [
                    f"### `{failure.target}`",
                    f"- Endpoint: `{failure.endpoint}`",
                    f"- Domain: `{failure.domain}`",
                    "",
                    _json_block(
                        {
                            "request": failure.request.to_dict(),
                            "response": failure.response,
                            "errorName": failure.error_name,
                            "errorMessage": failure.error_message,
                            "statusCode": failure.status_code,
                        }
                    ),
                    "",
                ]
            )

    _write(RESULTS_DIR / "failing-apis.md", "\n".join(lines))


def write_not_testable_report(results: list[SweepResult]) -> None:
    skipped = [result for result in results if result.status == "not-testable"]
    lines = [
        "# Not Testable With Current Plan",
        "",
        f"Generated at: {_now_iso()}",
        "",
        f"- Total not-testable APIs: `{len(skipped)}`",
        "",
    ]
    if not skipped:
        lines.append("None.")
    else:
        for result in skipped:
            lines.extend(
                [
                    f"## `{result.target}`",
                    f"- Endpoint: `{result.endpoint}`",
                    f"- Status code: `{result.status_code}`",
                    f"- Error: `{result.error_name}`",
                    f"- Message: `{result.error_message}`",
                    "",
                    _json_block({"request": result.request.to_dict()}),
                    "",
                ]
            )

    _write(RESULTS_DIR / "not-testable-with-current-plan.md", "\n".join(lines))


def write_inconsistent_responses_report(results: list[CompareResult]) -> None:
    mismatches, _ = split_compare_results(results)
    lines = [
        "# Inconsistent Responses",
        "",
        f"Generated at: {_now_iso()}",
        "",
        f"- Compared APIs: `{len(results)}`",
        f"- Mismatches: `{len(mismatches)}`",
        "",
    ]
    if not mismatches:
        lines.append("None.")
    else:
        for result in mismatches:
            lines.extend(
                [
                    f"## `{result.target}`",
                    f"- Endpoint: `{result.endpoint}`",
                    f"- Fallback used: `{result.fallback_reason or 'no'}`",
                    "",
                    _json_block(
                        {
                            "sdkRequest": result.sdk_request.to_dict(),
                            "directRequest": (
                                result.direct_request.to_dict()
                                if result.direct_request
                                else None
                            ),
                            "sdkResponse": result.sdk_response,
                            "directResponse": result.direct_response,
                            "diff": result.diff,
                        }
                    ),
                    "",
                ]
            )

    _write(RESULTS_DIR / "inconsistent-responses.md", "\n".join(lines))


def write_sdk_modules_catalog(
    records: list[SdkEndpointRecord],
    results: list[SweepResult],
) -> None:
    response_shapes = {
        result.target: result.response_shape
        for result in results
        if result.status == "success"
    }
    grouped: dict[str, list[SdkEndpointRecord]] = defaultdict(list)
    for record in records:
        grouped[record.module_name].append(record)

    lines = [
        "# SDK Modules Catalog",
        "",
        f"Generated at: {_now_iso()}",
        "",
    ]
    for module_name in sorted(grouped):
        lines.extend([f"## `{module_name}`", ""])
        for record in grouped[module_name]:
            lines.extend(
                [
                    f"### `{record.method_name}`",
                    f"- SDK call: `{record.target}`",
                    f"- Endpoint: `{record.endpoint}`",
                    f"- Normalized endpoint: `{record.normalized_endpoint}`",
                    f"- Domain: `{record.domain}`",
                    f"- Request encoding: `{record.request_encoding}`",
                    f"- Covered by Postman: "
                    f"`{'yes' if record.matched_postman_normalized_endpoint else 'no'}`",
                    "",
                    _json_block(
                        {
                            "requestFields": record.request_fields,
                            "pathParameters": record.path_parameters,
                            "exampleRequestBody": record.example_request_body,
                            "inferredResponseShape": response_shapes.get(record.target),
                        }
                    ),
                    "",
                ]
            )

    _write(CATALOG_DIR / "sdk-modules.md", "\n".join(lines))
