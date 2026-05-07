"""
Location namespace.

Geographic lookup and timezone resolution.
Use these endpoints to resolve place names to coordinates and timezones.
"""

from typing import Any


class LocationNamespace:
    """Location endpoints."""

    def __init__(self, http_client: Any) -> None:
        self.http = http_client

    def _post(self, endpoint: str, body: dict[str, Any]) -> Any:
        return self.http.post(endpoint, body)

    def get_geo_details(self, place: str, max_rows: int = 6) -> list[dict[str, Any]]:
        """
        Resolve geographic coordinates (lat, lon) from a place name.

        Args:
            place: Place name to search (e.g. "Mumbai", "New York")
            max_rows: Maximum number of results to return (default: 6)

        Returns:
            List of location matches with latitude, longitude, and place info
        """
        return self._post("geo_details", {"place": place, "maxRows": max_rows})

    def get_timezone(
        self,
        day: int,
        month: int,
        year: int,
        hour: int,
        min: int,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """
        Get the UTC timezone offset for a location and date, accounting for DST.

        Args:
            day: Day of date
            month: Month of date
            year: Year of date
            hour: Hour (0-23)
            min: Minute (0-59)
            lat: Latitude
            lon: Longitude

        Returns:
            Dictionary with tzone value (e.g. 5.5 for IST, -5.0 for EST)
        """
        return self._post(
            "timezone_with_dst",
            {
                "day": day,
                "month": month,
                "year": year,
                "hour": hour,
                "min": min,
                "lat": lat,
                "lon": lon,
            },
        )
