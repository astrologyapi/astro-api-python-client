"""Normalization and diff helpers shared by comparison and reporting flows."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit

VOLATILE_URL_KEYS = {"chart_url"}


def _strip_url_signature(value: str) -> str:
    """Drop volatile signed query tokens while preserving the stable URL path."""
    parts = urlsplit(value)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _normalize_volatile_chart_url(value: str) -> str:
    """Collapse generated chart asset names while preserving the stable bucket path."""
    stripped = _strip_url_signature(value)
    parts = urlsplit(stripped)
    path_parts = [part for part in parts.path.split("/") if part]
    if not path_parts:
        return stripped

    filename = path_parts[-1]
    extension = ""
    if "." in filename:
        extension = "." + filename.rsplit(".", 1)[1]
    path_parts[-1] = f"<generated>{extension}"
    normalized_path = "/" + "/".join(path_parts)
    return urlunsplit((parts.scheme, parts.netloc, normalized_path, "", ""))


def normalize_value(value: Any, path: tuple[str, ...] = ()) -> Any:
    """Normalize response values for stable equality checks."""
    key = path[-1] if path else ""

    if isinstance(value, dict):
        return {
            sub_key: normalize_value(value[sub_key], path + (sub_key,))
            for sub_key in sorted(value)
        }
    if isinstance(value, list):
        return [normalize_value(item, path + ("[]",)) for item in value]
    if isinstance(value, bytes):
        return {
            "type": "bytes",
            "length": len(value),
            "is_pdf": value.startswith(b"%PDF"),
        }
    if isinstance(value, str) and key in VOLATILE_URL_KEYS:
        return _normalize_volatile_chart_url(value)
    return value


def diff_values(left: Any, right: Any, path: str = "$") -> list[str]:
    """Produce a simple detailed diff between two normalized values."""
    left = normalize_value(left)
    right = normalize_value(right)

    if type(left) is not type(right):
        return [f"{path}: type mismatch {type(left).__name__} != {type(right).__name__}"]

    if isinstance(left, dict):
        diffs: list[str] = []
        left_keys = set(left)
        right_keys = set(right)
        for missing in sorted(left_keys - right_keys):
            diffs.append(f"{path}.{missing}: missing from direct response")
        for extra in sorted(right_keys - left_keys):
            diffs.append(f"{path}.{extra}: extra in direct response")
        for shared in sorted(left_keys & right_keys):
            diffs.extend(diff_values(left[shared], right[shared], f"{path}.{shared}"))
        return diffs

    if isinstance(left, list):
        diffs: list[str] = []
        if len(left) != len(right):
            diffs.append(f"{path}: list length mismatch {len(left)} != {len(right)}")
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            diffs.extend(diff_values(left_item, right_item, f"{path}[{index}]"))
        return diffs

    if left != right:
        return [f"{path}: {left!r} != {right!r}"]
    return []


def infer_shape(value: Any) -> Any:
    """Infer a compact response-shape snapshot for the module catalog."""
    if isinstance(value, dict):
        return {
            key: infer_shape(sub_value)
            for key, sub_value in sorted(value.items())
        }
    if isinstance(value, list):
        if not value:
            return []
        return [infer_shape(value[0])]
    if isinstance(value, bytes):
        return "bytes"
    if value is None:
        return "null"
    return type(value).__name__


def is_pdf_success(value: Any) -> bool:
    """Validate the shared PDF success rule."""
    if isinstance(value, bytes):
        return len(value) > 0 and value.startswith(b"%PDF")
    if isinstance(value, dict):
        return bool(value.get("status")) and bool(value.get("pdf_url"))
    return False
