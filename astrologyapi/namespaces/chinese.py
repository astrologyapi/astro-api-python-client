"""
Chinese astrology namespace.

Chinese zodiac sign and annual forecast.
"""

from typing import Any

from ..models import BirthData


class ChineseNamespace:
    """Chinese astrology endpoints."""

    def __init__(self, http_client: Any) -> None:
        self.http = http_client

    def _post(self, endpoint: str, body: dict[str, Any]) -> Any:
        return self.http.post(endpoint, body)

    def get_zodiac(self, data: BirthData) -> dict[str, Any]:
        """Chinese zodiac sign based on birth year, along with traits and compatibility."""
        return self._post("chinese_zodiac", data.to_dict())

    def get_year_forecast(self, data: BirthData) -> dict[str, Any]:
        """Chinese year forecast — annual predictions based on the Chinese zodiac sign."""
        return self._post("chinese_year_forecast", data.to_dict())
