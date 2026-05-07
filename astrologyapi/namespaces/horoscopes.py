"""
Horoscopes namespace.

Daily, next-day, previous-day, monthly sun-sign predictions plus nakshatra-based predictions.
"""

from __future__ import annotations

from typing import Any

from ..models import BirthData


def _timezone_body(timezone: float | None = None) -> dict[str, Any]:
    """Build the optional timezone body used by sun-sign helpers."""
    if timezone is None:
        return {}
    return {"timezone": timezone}


class HoroscopesNamespace:
    """Horoscope endpoints."""

    def __init__(self, http_client: Any) -> None:
        self.http = http_client

    def _post(self, endpoint: str, body: dict[str, Any]) -> Any:
        return self.http.post(endpoint, body)

    # ── Sun-Sign Predictions ───────────────────────────────────────────────────

    def get_daily(
        self,
        zodiac: str,
        timezone: float | None = None,
    ) -> dict[str, Any]:
        """Today's sun-sign horoscope prediction."""
        return self._post(
            f"sun_sign_prediction/daily/{zodiac}",
            _timezone_body(timezone),
        )

    def get_next(
        self,
        zodiac: str,
        timezone: float | None = None,
    ) -> dict[str, Any]:
        """Tomorrow's sun-sign horoscope prediction."""
        return self._post(
            f"sun_sign_prediction/daily/next/{zodiac}",
            _timezone_body(timezone),
        )

    def get_previous(
        self,
        zodiac: str,
        timezone: float | None = None,
    ) -> dict[str, Any]:
        """Yesterday's sun-sign horoscope prediction."""
        return self._post(
            f"sun_sign_prediction/daily/previous/{zodiac}",
            _timezone_body(timezone),
        )

    def get_daily_consolidated(
        self,
        zodiac: str,
        timezone: float | None = None,
    ) -> dict[str, Any]:
        """Consolidated daily horoscope covering all life areas."""
        return self._post(
            f"sun_sign_consolidated/daily/{zodiac}",
            _timezone_body(timezone),
        )

    def get_monthly(
        self,
        zodiac: str,
        timezone: float | None = None,
    ) -> dict[str, Any]:
        """Monthly sun-sign horoscope prediction."""
        return self._post(
            f"horoscope_prediction/monthly/{zodiac}",
            _timezone_body(timezone),
        )

    # ── Nakshatra Prediction ───────────────────────────────────────────────────

    def get_daily_nakshatra(self, data: BirthData) -> dict[str, Any]:
        """Daily prediction based on the birth Nakshatra (lunar mansion)."""
        return self._post("daily_nakshatra_prediction", data.to_dict())
