"""Load the shared language-agnostic QA scenario set from `testing/test-data`."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..models import BirthData, NumeroData, PDFBranding
from .paths import TEST_DATA_DIR


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def birth_from_raw(raw: dict[str, Any]) -> BirthData:
    """Convert a shared birth scenario into the SDK BirthData model."""
    return BirthData(
        day=raw["day"],
        month=raw["month"],
        year=raw["year"],
        hour=raw["hour"],
        min=raw["min"],
        lat=raw["lat"],
        lon=raw["lon"],
        tzone=raw["tzone"],
    )


def numero_from_raw(raw: dict[str, Any]) -> NumeroData:
    """Convert a numerology scenario into the SDK NumeroData model."""
    return NumeroData(
        day=raw["day"],
        month=raw["month"],
        year=raw["year"],
        name=raw.get("name", ""),
    )


def branding_from_raw(raw: dict[str, Any]) -> PDFBranding:
    """Convert the shared branding profile into the SDK PDFBranding model."""
    return PDFBranding(**raw)


@dataclass
class ScenarioBundle:
    """Canonical scenario bundle reused by inventory and live QA runs."""

    birth_primary: dict[str, Any]
    birth_secondary: dict[str, Any]
    birth_tertiary: dict[str, Any]
    couple: dict[str, Any]
    match: dict[str, Any]
    numerology_primary: dict[str, Any]
    numerology_secondary: dict[str, Any]
    pdf_branding: dict[str, Any]
    zodiac: dict[str, Any]


def load_test_data() -> ScenarioBundle:
    """Load the canonical cross-SDK QA scenarios from disk."""
    births = {
        path.stem: _read_json(path)
        for path in sorted((TEST_DATA_DIR / "birth").glob("*.json"))
    }
    numerology = {
        path.stem: _read_json(path)
        for path in sorted((TEST_DATA_DIR / "numerology").glob("*.json"))
    }

    return ScenarioBundle(
        birth_primary=births["standard"],
        birth_secondary=births["negative-timezone"],
        birth_tertiary=births["fractional-timezone"],
        couple=_read_json(TEST_DATA_DIR / "couple" / "basic-couple.json"),
        match=_read_json(TEST_DATA_DIR / "match" / "basic-match.json"),
        numerology_primary=numerology["basic"],
        numerology_secondary=numerology["alternate-name"],
        pdf_branding=_read_json(TEST_DATA_DIR / "pdf" / "basic-branding.json"),
        zodiac=_read_json(TEST_DATA_DIR / "zodiac" / "basic-sign-pairs.json"),
    )
