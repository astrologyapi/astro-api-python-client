"""Deterministic, comparison, and single-endpoint QA runners."""

from __future__ import annotations

import random
from typing import Any

from .._http import HttpClient
from .http_capture import RecordingHttpClient, serialize_value
from .invocation import build_module_registry, execute_plan, serialize_plan_args
from .models import CompareResult, InvocationPlan, RequestCapture, SweepResult
from .normalize import diff_values, infer_shape, is_pdf_success
from .postman import (
    build_direct_request_from_postman,
    build_direct_request_from_sdk_capture,
    find_postman_by_lookup,
    find_postman_match,
)
from .sdk_inventory import normalize_sdk_endpoint


def _enrich_capture(capture: RequestCapture, plan: InvocationPlan) -> RequestCapture:
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
    return capture


def _result_from_exception(
    plan: InvocationPlan,
    capture: RequestCapture,
    exc: Exception,
) -> SweepResult:
    status_code = getattr(exc, "status_code", None)
    status = "not-testable" if status_code in (402, 403) else "failure"
    return SweepResult(
        status=status,
        target=plan.target,
        module_name=plan.module_name,
        method_name=plan.method_name,
        endpoint=capture.endpoint,
        normalized_endpoint=capture.normalized_endpoint,
        domain=capture.domain,
        request=capture,
        response=None,
        error_name=exc.__class__.__name__,
        error_message=str(exc),
        status_code=status_code,
    )


def _execute_sdk_plan(
    recording: RecordingHttpClient,
    registry: dict[str, Any],
    plan: InvocationPlan,
) -> tuple[SweepResult, Any]:
    """Execute one SDK plan and keep the raw response for compare mode."""
    try:
        raw_response = execute_plan(plan, registry)
        capture = _enrich_capture(recording.last_capture, plan)  # type: ignore[arg-type]
        if capture.domain == "pdf" and not is_pdf_success(raw_response):
            return (
                SweepResult(
                    status="failure",
                    target=plan.target,
                    module_name=plan.module_name,
                    method_name=plan.method_name,
                    endpoint=capture.endpoint,
                    normalized_endpoint=capture.normalized_endpoint,
                    domain=capture.domain,
                    request=capture,
                    response=serialize_value(raw_response),
                    error_name="InvalidPDFResponse",
                    error_message=(
                        "Expected non-empty PDF bytes or a successful JSON "
                        "response containing pdf_url."
                    ),
                ),
                raw_response,
            )

        return (
            SweepResult(
                status="success",
                target=plan.target,
                module_name=plan.module_name,
                method_name=plan.method_name,
                endpoint=capture.endpoint,
                normalized_endpoint=capture.normalized_endpoint,
                domain=capture.domain,
                request=capture,
                response=serialize_value(raw_response),
                response_shape=infer_shape(raw_response),
            ),
            raw_response,
        )
    except Exception as exc:
        capture = recording.last_capture or RequestCapture(
            endpoint="unknown",
            domain="json",
            body_mode="json",
            body={},
            headers={},
            auth_style="unknown",
        )
        capture = _enrich_capture(capture, plan)
        return _result_from_exception(plan, capture, exc), None


def run_deterministic_sweep(
    config,
    plans: list[InvocationPlan],
) -> list[SweepResult]:
    """Execute the full deterministic SDK sweep against live credentials."""
    recording = RecordingHttpClient(
        HttpClient(config.api_key, timeout=config.timeout, retries=config.retries)
    )
    registry = build_module_registry(recording)
    results: list[SweepResult] = []

    try:
        for plan in plans:
            result, _ = _execute_sdk_plan(recording, registry, plan)
            results.append(result)
    finally:
        recording.close()

    return results


def _execute_direct_request(config, spec) -> dict[str, Any]:
    """Execute one direct API request using the shared auth inference rule."""
    recording = RecordingHttpClient(
        HttpClient(config.api_key, timeout=config.timeout, retries=config.retries)
    )
    try:
        raw_response = recording.post(
            spec.endpoint,
            spec.body,
            domain=spec.domain,
            body_mode=spec.body_mode,
        )
        capture = recording.last_capture
        if capture is None:
            raise RuntimeError("No direct-request capture recorded.")
        capture.normalized_endpoint = spec.normalized_endpoint

        if spec.domain == "pdf" and not is_pdf_success(raw_response):
            return {
                "status": "failure",
                "capture": capture,
                "response": serialize_value(raw_response),
                "raw_response": raw_response,
                "error_name": "InvalidPDFResponse",
                "error_message": (
                    "Expected non-empty PDF bytes or a successful JSON response "
                    "containing pdf_url."
                ),
                "status_code": None,
            }

        return {
            "status": "success",
            "capture": capture,
            "response": serialize_value(raw_response),
            "raw_response": raw_response,
            "error_name": None,
            "error_message": None,
            "status_code": None,
        }
    except Exception as exc:
        capture = recording.last_capture or RequestCapture(
            endpoint=spec.endpoint,
            domain=spec.domain,
            body_mode=spec.body_mode,
            body=spec.body,
            headers={},
            auth_style="unknown",
            normalized_endpoint=spec.normalized_endpoint,
        )
        return {
            "status": (
                "not-testable"
                if getattr(exc, "status_code", None) in (402, 403)
                else "failure"
            ),
            "capture": capture,
            "response": None,
            "raw_response": None,
            "error_name": exc.__class__.__name__,
            "error_message": str(exc),
            "status_code": getattr(exc, "status_code", None),
        }
    finally:
        recording.close()


def _should_fallback(spec) -> bool:
    return spec.source == "postman" and any(spec.divergence.values())


def _compare_payloads(domain: str, sdk_raw: Any, direct_raw: Any) -> list[str]:
    if domain == "pdf":
        if is_pdf_success(sdk_raw) and is_pdf_success(direct_raw):
            return []
        return ["PDF success contract mismatch."]
    return diff_values(sdk_raw, direct_raw)


def _compare_single_plan(config, plan, postman_entries) -> CompareResult:
    """Execute one SDK plan and compare it with a direct API request."""
    recording = RecordingHttpClient(
        HttpClient(config.api_key, timeout=config.timeout, retries=config.retries)
    )
    registry = build_module_registry(recording)

    try:
        sdk_result, sdk_raw = _execute_sdk_plan(recording, registry, plan)
    finally:
        recording.close()

    if sdk_result.status != "success":
        return CompareResult(
            status=sdk_result.status,
            target=plan.target,
            endpoint=sdk_result.endpoint,
            normalized_endpoint=sdk_result.normalized_endpoint,
            sdk_request=sdk_result.request,
            direct_request=None,
            sdk_response=sdk_result.response,
            error_name=sdk_result.error_name,
            error_message=sdk_result.error_message,
            status_code=sdk_result.status_code,
        )

    matched_postman = find_postman_match(postman_entries, sdk_result.request)
    direct_spec = (
        build_direct_request_from_postman(matched_postman, sdk_result.request)
        if matched_postman
        else build_direct_request_from_sdk_capture(sdk_result.request)
    )
    direct_result = _execute_direct_request(config, direct_spec)
    fallback_reason = None
    diff = (
        _compare_payloads(sdk_result.domain, sdk_raw, direct_result["raw_response"])
        if direct_result["status"] == "success"
        else [direct_result["error_message"] or "Direct request failed."]
    )

    if (direct_result["status"] != "success" or diff) and _should_fallback(direct_spec):
        fallback_reason = (
            "Postman request shape diverged from the SDK-captured request: "
            + ", ".join(
                f"{key}={','.join(values) or 'none'}"
                for key, values in direct_spec.divergence.items()
                if values
            )
        )
        fallback_spec = build_direct_request_from_sdk_capture(sdk_result.request)
        fallback_result = _execute_direct_request(config, fallback_spec)
        direct_spec = fallback_spec
        direct_result = fallback_result
        diff = (
            _compare_payloads(sdk_result.domain, sdk_raw, fallback_result["raw_response"])
            if fallback_result["status"] == "success"
            else [fallback_result["error_message"] or "Fallback direct request failed."]
        )

    status = direct_result["status"]
    if status == "success" and diff:
        status = "failure"

    return CompareResult(
        status=status,
        target=plan.target,
        endpoint=sdk_result.endpoint,
        normalized_endpoint=sdk_result.normalized_endpoint,
        sdk_request=sdk_result.request,
        direct_request=direct_result["capture"],
        sdk_response=sdk_result.response,
        direct_response=direct_result["response"],
        diff=diff,
        fallback_reason=fallback_reason,
        error_name=direct_result["error_name"],
        error_message=direct_result["error_message"],
        status_code=direct_result["status_code"],
    )


def run_randomized_compare(
    config,
    plans: list[InvocationPlan],
    postman_entries,
    sample_size: int = 25,
    seed: int | None = None,
) -> list[CompareResult]:
    """Run a randomized SDK-vs-direct comparison sample."""
    if not plans:
        return []

    rng = random.Random(seed)
    sampled_plans = (
        rng.sample(plans, min(sample_size, len(plans)))
        if sample_size < len(plans)
        else list(plans)
    )
    return [
        _compare_single_plan(config, plan, postman_entries)
        for plan in sampled_plans
    ]


def run_single_endpoint_debug(
    config,
    plans: list[InvocationPlan],
    postman_entries,
    sdk_target: str,
    direct_target_lookup: str | None = None,
) -> CompareResult:
    """Run one SDK target side-by-side with a direct API request."""
    plan = next((item for item in plans if item.target == sdk_target), None)
    if plan is None:
        raise ValueError(f"Unknown SDK target: {sdk_target}")

    if not direct_target_lookup:
        return _compare_single_plan(config, plan, postman_entries)

    recording = RecordingHttpClient(
        HttpClient(config.api_key, timeout=config.timeout, retries=config.retries)
    )
    registry = build_module_registry(recording)
    try:
        sdk_result, sdk_raw = _execute_sdk_plan(recording, registry, plan)
    finally:
        recording.close()

    if sdk_result.status != "success":
        return CompareResult(
            status=sdk_result.status,
            target=plan.target,
            endpoint=sdk_result.endpoint,
            normalized_endpoint=sdk_result.normalized_endpoint,
            sdk_request=sdk_result.request,
            direct_request=None,
            sdk_response=sdk_result.response,
            error_name=sdk_result.error_name,
            error_message=sdk_result.error_message,
            status_code=sdk_result.status_code,
        )

    matched_postman = find_postman_by_lookup(postman_entries, direct_target_lookup)
    if not matched_postman:
        raise ValueError(f"No Postman endpoint matched lookup `{direct_target_lookup}`")

    direct_spec = build_direct_request_from_postman(matched_postman, sdk_result.request)
    direct_result = _execute_direct_request(config, direct_spec)
    diff = (
        _compare_payloads(sdk_result.domain, sdk_raw, direct_result["raw_response"])
        if direct_result["status"] == "success"
        else [direct_result["error_message"] or "Direct request failed."]
    )

    if (direct_result["status"] != "success" or diff) and _should_fallback(direct_spec):
        fallback_spec = build_direct_request_from_sdk_capture(sdk_result.request)
        direct_result = _execute_direct_request(config, fallback_spec)
        diff = (
            _compare_payloads(sdk_result.domain, sdk_raw, direct_result["raw_response"])
            if direct_result["status"] == "success"
            else [direct_result["error_message"] or "Fallback direct request failed."]
        )

    status = direct_result["status"]
    if status == "success" and diff:
        status = "failure"

    return CompareResult(
        status=status,
        target=sdk_result.target,
        endpoint=sdk_result.endpoint,
        normalized_endpoint=sdk_result.normalized_endpoint,
        sdk_request=sdk_result.request,
        direct_request=direct_result["capture"],
        sdk_response=sdk_result.response,
        direct_response=direct_result["response"],
        diff=diff,
        error_name=direct_result["error_name"],
        error_message=direct_result["error_message"],
        status_code=direct_result["status_code"],
    )
