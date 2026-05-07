"""
Lal Kitab astrology namespace.

Lal Kitab is an unconventional system of Vedic astrology and palmistry
originating in Punjab, with a unique house system and remedies.
"""

from typing import Any

from ..models import BirthData


def _lal_kitab_body(
    data: BirthData,
    ayanamsha: str = "LAHIRI",
) -> dict[str, Any]:
    """Add Lal Kitab parity defaults from the shared QA assets."""
    body = data.to_dict()
    body["ayanamsha"] = ayanamsha
    return body


class LalKitabNamespace:
    """Lal Kitab astrology endpoints."""

    def __init__(self, http_client: Any) -> None:
        self.http = http_client

    def _post(self, endpoint: str, body: dict[str, Any]) -> Any:
        return self.http.post(endpoint, body, body_mode="form")

    def get_horoscope(
        self,
        data: BirthData,
        ayanamsha: str = "LAHIRI",
    ) -> dict[str, Any]:
        """Full Lal Kitab horoscope with planetary positions in the Lal Kitab house system."""
        return self._post("lalkitab_horoscope", _lal_kitab_body(data, ayanamsha))

    def get_debts(
        self,
        data: BirthData,
        ayanamsha: str = "LAHIRI",
    ) -> dict[str, Any]:
        """Lal Kitab debts (Rin) analysis — identifies karmic debts."""
        return self._post("lalkitab_debts", _lal_kitab_body(data, ayanamsha))

    def get_remedies(
        self,
        planet: str,
        data: BirthData,
        ayanamsha: str = "LAHIRI",
    ) -> dict[str, Any]:
        """Lal Kitab remedies for a specific planet."""
        return self._post(
            f"lalkitab_remedies/{planet}",
            _lal_kitab_body(data, ayanamsha),
        )

    def get_houses(
        self,
        data: BirthData,
        ayanamsha: str = "LAHIRI",
    ) -> dict[str, Any]:
        """Lal Kitab house analysis — significance and effects of each house."""
        return self._post("lalkitab_houses", _lal_kitab_body(data, ayanamsha))

    def get_planets(
        self,
        data: BirthData,
        ayanamsha: str = "LAHIRI",
    ) -> dict[str, Any]:
        """Lal Kitab planetary positions with house-based interpretations."""
        return self._post("lalkitab_planets", _lal_kitab_body(data, ayanamsha))
