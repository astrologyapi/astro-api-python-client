"""
Numerology namespace.

Vedic (Pythagorean/Indian) and Western numerological calculations.
"""

from typing import Any, Optional

from ..models import NumeroData


def _numero_body(data: NumeroData) -> dict[str, Any]:
    """Shared Vedic numerology request body."""
    return data.to_dict()


def _western_numerology_body(
    data: NumeroData,
    full_name: Optional[str] = None,
) -> dict[str, Any]:
    """Map SDK numerology data to the live Western numerology contract."""
    body = {
        "date": data.day,
        "month": data.month,
        "year": data.year,
    }
    resolved_name = full_name or getattr(data, "name", "")
    if resolved_name:
        body["full_name"] = resolved_name
    return body


class NumerologyNamespace:
    """Numerology endpoints."""

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

    # ── Vedic Numerology ───────────────────────────────────────────────────────

    def get_table(self, data: NumeroData) -> dict[str, Any]:
        """Vedic numerology table — Psychic, Destiny, Name, and Kua numbers."""
        return self._post("numero_table", _numero_body(data), body_mode="form")

    def get_report(self, data: NumeroData) -> dict[str, Any]:
        """Comprehensive Vedic numerology report with personality and life analysis."""
        return self._post("numero_report", _numero_body(data), body_mode="form")

    def get_fav_time(self, data: NumeroData) -> dict[str, Any]:
        """Favourable time periods based on numerological cycles."""
        return self._post("numero_fav_time", _numero_body(data), body_mode="form")

    def get_place_vastu(self, data: NumeroData) -> dict[str, Any]:
        """Vastu and place suitability based on numerology."""
        return self._post("numero_place_vastu", _numero_body(data), body_mode="form")

    def get_fasts_report(self, data: NumeroData) -> dict[str, Any]:
        """Recommended fasts (vrats) based on numerological analysis."""
        return self._post("numero_fasts_report", _numero_body(data), body_mode="form")

    def get_fav_lord(self, data: NumeroData) -> dict[str, Any]:
        """Favourable deity / ruling lord based on numerology."""
        return self._post("numero_fav_lord", _numero_body(data), body_mode="form")

    def get_fav_mantra(self, data: NumeroData) -> dict[str, Any]:
        """Recommended mantras based on numerological profile."""
        return self._post("numero_fav_mantra", _numero_body(data), body_mode="form")

    def get_daily_prediction(self, data: NumeroData) -> dict[str, Any]:
        """Daily numerology prediction based on personal number cycles."""
        return self._post(
            "numero_prediction/daily",
            _numero_body(data),
            body_mode="form",
        )

    # ── Western Numerology ─────────────────────────────────────────────────────

    def get_numerological_numbers(
        self,
        data: NumeroData,
        *,
        full_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """All core Western numerological numbers: Life Path, Expression, Soul Urge, etc."""
        return self._post(
            "numerological_numbers",
            _western_numerology_body(data, full_name),
            body_mode="json",
        )

    def get_lifepath_number(
        self,
        data: NumeroData,
        *,
        full_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Life Path Number — the most significant number in Western numerology."""
        return self._post(
            "lifepath_number",
            _western_numerology_body(data, full_name),
            body_mode="json",
        )

    def get_personality_number(
        self,
        data: NumeroData,
        *,
        full_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Personality Number (derived from consonants in the name)."""
        return self._post(
            "personality_number",
            _western_numerology_body(data, full_name),
            body_mode="json",
        )

    def get_expression_number(
        self,
        data: NumeroData,
        *,
        full_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Expression (Destiny) Number — derived from the full name."""
        return self._post(
            "expression_number",
            _western_numerology_body(data, full_name),
            body_mode="json",
        )

    def get_soul_urge_number(
        self,
        data: NumeroData,
        *,
        full_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Soul Urge (Heart's Desire) Number — derived from vowels in the name."""
        return self._post(
            "soul_urge_number",
            _western_numerology_body(data, full_name),
            body_mode="json",
        )

    def get_challenge_numbers(
        self,
        data: NumeroData,
        *,
        full_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Challenge Numbers — obstacles to overcome in each life stage."""
        return self._post(
            "challenge_numbers",
            _western_numerology_body(data, full_name),
            body_mode="json",
        )

    def get_personal_day(
        self,
        data: NumeroData,
        *,
        full_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Personal Day Number — the numerological energy of a specific day."""
        return self._post(
            "personal_day_prediction",
            _western_numerology_body(data, full_name),
            body_mode="json",
        )

    def get_personal_month(
        self,
        data: NumeroData,
        *,
        full_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Personal Month Number — the numerological theme for the current month."""
        return self._post(
            "personal_month_prediction",
            _western_numerology_body(data, full_name),
            body_mode="json",
        )

    def get_personal_year(
        self,
        data: NumeroData,
        *,
        full_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Personal Year Number — the overarching theme and energy for the current year."""
        return self._post(
            "personal_year_prediction",
            _western_numerology_body(data, full_name),
            body_mode="json",
        )
