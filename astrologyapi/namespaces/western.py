"""
Western (Tropical) astrology namespace.

Covers birth charts, house systems, solar return, synastry,
personality reports, moon phases, and compatibility.
"""

from __future__ import annotations

from typing import Any

from ..models import BirthData


def _flatten_couple_data(person1: BirthData, person2: BirthData) -> dict[str, Any]:
    """Flatten couple birth data into p_/s_ prefixed keys."""
    p = person1.to_dict()
    s = person2.to_dict()
    return {
        "p_day": p["day"],
        "p_month": p["month"],
        "p_year": p["year"],
        "p_hour": p["hour"],
        "p_min": p["min"],
        "p_lat": p["lat"],
        "p_lon": p["lon"],
        "p_tzone": p["tzone"],
        "s_day": s["day"],
        "s_month": s["month"],
        "s_year": s["year"],
        "s_hour": s["hour"],
        "s_min": s["min"],
        "s_lat": s["lat"],
        "s_lon": s["lon"],
        "s_tzone": s["tzone"],
    }


def _solar_return_body(
    data: BirthData,
    solar_year: int | None = None,
    year: int | None = None,
) -> dict[str, Any]:
    """Normalize solar return inputs to the shared `solar_year` contract."""
    body = data.to_dict()
    resolved_year = solar_year if solar_year is not None else year
    if resolved_year is not None:
        body["solar_year"] = resolved_year
    return body


class WesternNamespace:
    """Western (tropical) astrology endpoints."""

    http: Any

    def __init__(self, http_client: Any) -> None:
        self.http = http_client

    def _post(
        self,
        endpoint: str,
        body: dict[str, Any],
        body_mode: str = "json",
    ) -> Any:
        return self.http.post(endpoint, body, body_mode=body_mode)

    # ── Core Birth Chart ───────────────────────────────────────────────────────

    def get_planets(self, data: BirthData) -> dict[str, Any]:
        """Tropical (Western) planetary positions with sign, house, and degree."""
        return self._post("planets/tropical", data.to_dict())

    def get_house_cusps(self, data: BirthData) -> dict[str, Any]:
        """Tropical house cusps using the default (Placidus) house system."""
        return self._post("house_cusps/tropical", data.to_dict())

    def get_horoscope(self, data: BirthData) -> dict[str, Any]:
        """Complete Western horoscope — planets, houses, aspects, and highlights."""
        return self._post("western_horoscope", data.to_dict())

    def get_natal_wheel_chart(self, data: BirthData) -> dict[str, Any]:
        """SVG natal wheel chart for embedding or display."""
        return self._post(
            "natal_wheel_chart",
            data.to_dict(),
            body_mode="form",
        )

    def get_natal_interpretation(self, data: BirthData) -> dict[str, Any]:
        """Narrative interpretation of the natal chart."""
        return self._post("natal_chart_interpretation", data.to_dict())

    # ── House Reports ──────────────────────────────────────────────────────────

    def get_house_cusps_report(self, data: BirthData) -> dict[str, Any]:
        """Interpretive descriptions for all house cusps."""
        return self._post("house_cusps_report/tropical", data.to_dict())

    def get_natal_house_cusp_report(self, data: BirthData) -> dict[str, Any]:
        """Natal house cusp report with planetary influence."""
        return self._post("natal_house_cusp_report", data.to_dict())

    def get_ascendant_report(self, data: BirthData) -> dict[str, Any]:
        """Interpretive report for the Western ascendant sign."""
        return self._post("general_ascendant_report/tropical", data.to_dict())

    def get_sign_report(self, planet: str, data: BirthData) -> dict[str, Any]:
        """Report for a planet's sign placement in the tropical zodiac."""
        return self._post(f"general_sign_report/tropical/{planet}", data.to_dict())

    def get_house_report(self, planet: str, data: BirthData) -> dict[str, Any]:
        """Report for a planet's house placement in the tropical chart."""
        return self._post(f"general_house_report/tropical/{planet}", data.to_dict())

    # ── Moon ───────────────────────────────────────────────────────────────────

    def get_moon_phase(self, data: BirthData) -> dict[str, Any]:
        """Current moon phase and its astrological significance."""
        return self._post("moon_phase_report", data.to_dict())

    def get_lunar_metrics(self, data: BirthData) -> dict[str, Any]:
        """Lunar metrics — moon sign, nakshatra, tithi, and more."""
        return self._post("lunar_metrics", data.to_dict())

    # ── Solar Return ───────────────────────────────────────────────────────────

    def get_solar_return_details(
        self,
        data: BirthData,
        solar_year: int | None = None,
        year: int | None = None,
    ) -> dict[str, Any]:
        """Solar Return chart details — the chart for when the Sun returns to its natal position."""
        return self._post(
            "solar_return_details",
            _solar_return_body(data, solar_year, year),
        )

    def get_solar_return_planets(
        self,
        data: BirthData,
        solar_year: int | None = None,
        year: int | None = None,
    ) -> dict[str, Any]:
        """Planetary positions in the Solar Return chart."""
        return self._post(
            "solar_return_planets",
            _solar_return_body(data, solar_year, year),
        )

    def get_solar_return_house_cusps(
        self,
        data: BirthData,
        solar_year: int | None = None,
        year: int | None = None,
    ) -> dict[str, Any]:
        """House cusps in the Solar Return chart."""
        return self._post(
            "solar_return_house_cusps",
            _solar_return_body(data, solar_year, year),
        )

    def get_solar_return_planet_report(
        self,
        data: BirthData,
        solar_year: int | None = None,
        year: int | None = None,
    ) -> dict[str, Any]:
        """Interpretive report for each planet in the Solar Return chart."""
        return self._post(
            "solar_return_planet_report",
            _solar_return_body(data, solar_year, year),
        )

    def get_solar_return_planet_aspects(
        self,
        data: BirthData,
        solar_year: int | None = None,
        year: int | None = None,
    ) -> dict[str, Any]:
        """Aspects formed between Solar Return planets and natal planets."""
        return self._post(
            "solar_return_planet_aspects",
            _solar_return_body(data, solar_year, year),
        )

    def get_solar_return_aspects_report(
        self,
        data: BirthData,
        solar_year: int | None = None,
        year: int | None = None,
    ) -> dict[str, Any]:
        """Comprehensive aspects report for the Solar Return chart."""
        return self._post(
            "solar_return_aspects_report",
            _solar_return_body(data, solar_year, year),
        )

    # ── Personality & Life Reports ─────────────────────────────────────────────

    def get_personality(self, data: BirthData) -> dict[str, Any]:
        """Personality analysis based on the tropical natal chart."""
        return self._post("personality_report/tropical", data.to_dict())

    def get_romantic_personality(self, data: BirthData) -> dict[str, Any]:
        """Romantic personality — how the person behaves in love and relationships."""
        return self._post("romantic_personality_report/tropical", data.to_dict())

    def get_friendship(
        self,
        person1: BirthData,
        person2: BirthData,
    ) -> dict[str, Any]:
        """Friendship profile — social style and compatible friend types."""
        return self._post(
            "friendship_report/tropical",
            _flatten_couple_data(person1, person2),
        )

    def get_romantic_forecast(self, data: BirthData) -> dict[str, Any]:
        """Romantic forecast for the current period."""
        return self._post("romantic_forecast_report/tropical", data.to_dict())

    def get_karma_destiny(
        self,
        person1: BirthData,
        person2: BirthData,
    ) -> dict[str, Any]:
        """Karma and destiny report — life lessons and past-life influences."""
        return self._post(
            "karma_destiny_report/tropical",
            _flatten_couple_data(person1, person2),
        )

    # ── Compatibility ──────────────────────────────────────────────────────────

    def get_zodiac_compatibility(
        self, zodiac: str, partner_zodiac: str
    ) -> dict[str, Any]:
        """Sun-sign compatibility score and analysis between two zodiac signs."""
        return self._post(f"zodiac_compatibility/{zodiac}/{partner_zodiac}", {})

    def get_synastry(self, person1: BirthData, person2: BirthData) -> dict[str, Any]:
        """Synastry horoscope — aspect analysis between two natal charts."""
        return self._post("synastry_horoscope", _flatten_couple_data(person1, person2))

    def get_composite(self, person1: BirthData, person2: BirthData) -> dict[str, Any]:
        """Composite chart — the midpoint chart representing the relationship itself."""
        return self._post("composite_horoscope", _flatten_couple_data(person1, person2))
