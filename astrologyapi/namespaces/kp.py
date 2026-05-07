"""
KP (Krishnamurti Paddhati) astrology namespace.

KP is a precision system based on the stellar/sub-lord theory
using Placidus house cusps.
"""

from __future__ import annotations

from typing import Any

from ..models import BirthData


def _kp_body(
    data: BirthData,
    ayanamsha: str = "LAHIRI",
    aspects: bool | None = None,
) -> dict[str, Any]:
    """Add KP runtime defaults required by the shared QA assets."""
    body = data.to_dict()
    body["ayanamsha"] = ayanamsha
    if aspects is not None:
        body["aspects"] = aspects
    return body


class KPNamespace:
    """KP astrology endpoints."""

    def __init__(self, http_client: Any) -> None:
        self.http = http_client

    def _post(
        self,
        endpoint: str,
        body: dict[str, Any],
        body_mode: str = "json",
    ) -> Any:
        return self.http.post(endpoint, body, body_mode=body_mode)

    def get_planets(
        self,
        data: BirthData,
        ayanamsha: str = "LAHIRI",
    ) -> dict[str, Any]:
        """KP planetary positions with sub-lord, star-lord, and sign data."""
        return self._post(
            "kp_planets",
            _kp_body(data, ayanamsha),
            body_mode="form",
        )

    def get_house_cusps(
        self,
        data: BirthData,
        ayanamsha: str = "LAHIRI",
    ) -> dict[str, Any]:
        """KP house cusps with sub-lord and star-lord for each cusp."""
        return self._post(
            "kp_house_cusps",
            _kp_body(data, ayanamsha),
            body_mode="form",
        )

    def get_birth_chart(
        self,
        data: BirthData,
        ayanamsha: str = "LAHIRI",
    ) -> dict[str, Any]:
        """Full KP birth chart including planets and house cusps."""
        return self._post(
            "kp_birth_chart",
            _kp_body(data, ayanamsha),
            body_mode="form",
        )

    def get_house_significator(
        self,
        data: BirthData,
        ayanamsha: str = "LAHIRI",
    ) -> dict[str, Any]:
        """KP significators for each house (1–12)."""
        return self._post(
            "kp_house_significator",
            _kp_body(data, ayanamsha),
            body_mode="form",
        )

    def get_planet_significator(
        self,
        data: BirthData,
        ayanamsha: str = "LAHIRI",
    ) -> dict[str, Any]:
        """KP significators for each planet."""
        return self._post(
            "kp_planet_significator",
            _kp_body(data, ayanamsha),
            body_mode="form",
        )

    def get_horoscope(
        self,
        data: BirthData,
        ayanamsha: str = "LAHIRI",
        aspects: bool = True,
    ) -> dict[str, Any]:
        """Complete KP horoscope combining all KP chart data."""
        return self._post(
            "kp_horoscope",
            _kp_body(data, ayanamsha, aspects),
            body_mode="form",
        )
