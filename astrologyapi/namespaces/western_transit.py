"""
Western Transit namespace.

Tropical transit calculations — how current planetary positions
interact with the natal chart.
"""

from typing import Any

from ..models import BirthData


class WesternTransitNamespace:
    """Western transit endpoints."""

    def __init__(self, http_client: Any) -> None:
        self.http = http_client

    def _post(self, endpoint: str, body: dict[str, Any]) -> Any:
        return self.http.post(endpoint, body)

    # ── Current-Sky Transits ───────────────────────────────────────────────────

    def get_daily(self, data: BirthData) -> dict[str, Any]:
        """Daily tropical transit positions — where the planets are today."""
        return self._post("tropical_transits/daily", data.to_dict())

    def get_weekly(self, data: BirthData) -> dict[str, Any]:
        """Weekly tropical transit overview."""
        return self._post("tropical_transits/weekly", data.to_dict())

    def get_monthly(self, data: BirthData) -> dict[str, Any]:
        """Monthly tropical transit positions and highlights."""
        return self._post("tropical_transits/monthly", data.to_dict())

    # ── Natal Transits ─────────────────────────────────────────────────────────

    def get_natal_daily(self, data: BirthData) -> dict[str, Any]:
        """Daily natal transits — aspects current planets make to the natal chart."""
        return self._post("natal_transits/daily", data.to_dict())

    def get_natal_weekly(self, data: BirthData) -> dict[str, Any]:
        """Weekly natal transits — personalised weekly transit aspects."""
        return self._post("natal_transits/weekly", data.to_dict())
