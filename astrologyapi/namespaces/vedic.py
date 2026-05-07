"""
Vedic astrology namespace.

Covers birth charts, divisional charts (D1–D60), all Dasha systems
(Vimshottari, Char, Yogini), Panchang, Muhurta, Matchmaking,
Varshaphal, Doshas, Remedies, and interpretive reports.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..models import BirthData

DEFAULT_AYANAMSHA = "LAHIRI"


def _birth_body(
    data: BirthData,
    ayanamsha: str | None = None,
    **extras: Any,
) -> dict[str, Any]:
    """Build a request body from birth data plus optional runtime defaults."""
    body = data.to_dict()
    if ayanamsha is not None:
        body["ayanamsha"] = ayanamsha
    for key, value in extras.items():
        if value is not None:
            body[key] = value
    return body


def _flatten_match_data(
    male: BirthData,
    female: BirthData,
    ayanamsha: str = DEFAULT_AYANAMSHA,
) -> dict[str, Any]:
    """Flatten compatibility data into the live match endpoint contract."""
    return {
        "m_day": male.day,
        "m_month": male.month,
        "m_year": male.year,
        "m_hour": male.hour,
        "m_min": male.min,
        "m_lat": male.lat,
        "m_lon": male.lon,
        "m_tzone": male.tzone,
        "f_day": female.day,
        "f_month": female.month,
        "f_year": female.year,
        "f_hour": female.hour,
        "f_min": female.min,
        "f_lat": female.lat,
        "f_lon": female.lon,
        "f_tzone": female.tzone,
        "ayanamsha": ayanamsha,
    }


def _varshaphal_body(
    data: BirthData,
    varshaphal_year: int | None = None,
    year_count: int | None = None,
    ayanamsha: str = DEFAULT_AYANAMSHA,
) -> dict[str, Any]:
    """Normalize Varshaphal requests to the shared parity contract."""
    resolved_year = varshaphal_year
    if resolved_year is None and year_count is not None:
        resolved_year = data.year + year_count
    if resolved_year is None:
        resolved_year = datetime.now().year
    return _birth_body(
        data,
        ayanamsha=ayanamsha,
        varshaphal_year=resolved_year,
    )


def _papasamyam_body(
    data: BirthData,
    full_name: str,
    ayanamsha: str = DEFAULT_AYANAMSHA,
    date: int | None = None,
) -> dict[str, Any]:
    """Build the single-profile Papasamyam request documented in the tracker."""
    resolved_date = data.day if date is None else date
    return {
        "full_name": full_name,
        "day": data.day,
        "date": resolved_date,
        "month": data.month,
        "year": data.year,
        "hour": data.hour,
        "min": data.min,
        "lat": data.lat,
        "lon": data.lon,
        "tzone": data.tzone,
        "ayanamsha": ayanamsha,
    }


class VedicNamespace:
    """Vedic astrology endpoints."""

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

    # ── Birth Data ─────────────────────────────────────────────────────────────

    def get_birth_details(self, data: BirthData) -> dict[str, Any]:
        """Core birth chart summary: ascendant, sun sign, moon sign, nakshatra."""
        return self._post("birth_details", data.to_dict())

    def get_astro_details(self, data: BirthData) -> dict[str, Any]:
        """Extended astrological details including yoga, karana, and tithi."""
        return self._post("astro_details", data.to_dict())

    def get_ayanamsha(self, data: BirthData) -> dict[str, Any]:
        """Ayanamsha value for the given birth date and time."""
        return self._post("ayanamsha", data.to_dict())

    # ── Planets ────────────────────────────────────────────────────────────────

    def get_planets(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Planetary positions with sign, nakshatra, house, and degree."""
        return self._post("planets", _birth_body(data, ayanamsha))

    def get_extended_planets(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Extended planetary data including retrograde status, speed, and dignity."""
        return self._post("planets/extended", _birth_body(data, ayanamsha))

    def get_planet_ashtak(
        self,
        planet: str,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Ashtak Varga table for a specific planet."""
        return self._post(
            f"planet_ashtak/{planet}",
            _birth_body(data, ayanamsha),
        )

    def get_sarvashtak(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Sarvashtakavarga (combined Ashtak Varga) table."""
        return self._post("sarvashtak", _birth_body(data, ayanamsha))

    def get_ghat_chakra(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Ghat Chakra calculation."""
        return self._post("ghat_chakra", _birth_body(data, ayanamsha))

    # ── Horoscope Charts ───────────────────────────────────────────────────────

    def get_chart(
        self,
        chart_id: str,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """
        Divisional chart data (D1 = Lagna, D9 = Navamsa, D10 = Dashamsa, etc.).
        """
        return self._post(f"horo_chart/{chart_id}", _birth_body(data, ayanamsha))

    def get_chart_image(
        self,
        chart_id: str,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """SVG/image representation of a divisional chart."""
        return self._post(
            f"horo_chart_image/{chart_id}",
            _birth_body(data, ayanamsha),
        )

    def get_extended_chart(
        self,
        data: BirthData,
        chart_id: str = "D1",
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Extended chart data, defaulting to the D1 chart for compatibility."""
        return self._post(
            f"horo_chart_extended/{chart_id}",
            _birth_body(data, ayanamsha),
        )

    # ── Vimshottari Dasha ──────────────────────────────────────────────────────

    def get_current_dasha(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Current running Vimshottari Maha Dasha, Antardasha, and Pratyantardasha."""
        return self._post("current_vdasha", _birth_body(data, ayanamsha))

    def get_major_dasha(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Full Vimshottari Maha Dasha sequence (all 120-year cycle)."""
        return self._post("major_vdasha", _birth_body(data, ayanamsha))

    def get_sub_dasha(
        self,
        maha_dasha: str,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Sub-dashas (Antardasha) within a given Maha Dasha."""
        return self._post(
            f"sub_vdasha/{maha_dasha}",
            _birth_body(data, ayanamsha),
        )

    def get_sub_sub_dasha(
        self,
        maha_dasha: str,
        antar_dasha: str,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Sub-sub-dashas (Pratyantardasha) for a given dasha pair."""
        return self._post(
            f"sub_sub_vdasha/{maha_dasha}/{antar_dasha}",
            _birth_body(data, ayanamsha),
        )

    def get_sub_sub_sub_dasha(
        self,
        maha_dasha: str,
        antar_dasha: str,
        pratyantar_dasha: str,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Sub-sub-sub-dashas (Sookshma) for the provided dasha path."""
        return self._post(
            f"sub_sub_sub_vdasha/{maha_dasha}/{antar_dasha}/{pratyantar_dasha}",
            _birth_body(data, ayanamsha),
        )

    def get_sub_sub_sub_sub_dasha(
        self,
        maha_dasha: str,
        antar_dasha: str,
        pratyantar_dasha: str,
        sookshma_dasha: str,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Sub-sub-sub-sub-dashas (Prana) for the provided dasha path."""
        return self._post(
            "sub_sub_sub_sub_vdasha/"
            f"{maha_dasha}/{antar_dasha}/{pratyantar_dasha}/{sookshma_dasha}",
            _birth_body(data, ayanamsha),
        )

    # ── Char Dasha (Jaimini) ───────────────────────────────────────────────────

    def get_current_char_dasha(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Current running Char Dasha and Antardasha."""
        return self._post(
            "current_chardasha",
            _birth_body(data, ayanamsha),
            body_mode="form",
        )

    def get_major_char_dasha(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """All Char Maha Dashas in sequence."""
        return self._post(
            "major_chardasha",
            _birth_body(data, ayanamsha),
            body_mode="form",
        )

    def get_sub_char_dasha(
        self,
        maha_dasha: str,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Sub-dashas within a specific Char sign period such as `ARIES`."""
        return self._post(
            f"sub_chardasha/{maha_dasha}",
            _birth_body(data, ayanamsha),
            body_mode="form",
        )

    # ── Yogini Dasha ───────────────────────────────────────────────────────────

    def get_current_yogini_dasha(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Current running Yogini Dasha and sub-period."""
        return self._post(
            "current_yogini_dasha",
            _birth_body(data, ayanamsha),
            body_mode="form",
        )

    # ── Doshas ─────────────────────────────────────────────────────────────────

    def get_kalsarpa_dosha(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Kalsarpa Dosha analysis — type, strength, and remedies."""
        return self._post("kalsarpa_details", _birth_body(data, ayanamsha))

    def get_manglik(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Whether Mangal (Mars) Dosha is present and its effects."""
        return self._post("manglik", _birth_body(data, ayanamsha))

    def get_sadhesati_status(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Current Sade Sati phase status (rising, peak, or setting)."""
        return self._post(
            "sadhesati_current_status",
            _birth_body(data, ayanamsha),
        )

    def get_sadhesati_life_details(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Full Sade Sati life timeline — all past and future occurrences."""
        return self._post(
            "sadhesati_life_details",
            _birth_body(data, ayanamsha),
        )

    def get_pitra_dosha(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Pitra Dosha analysis and significance."""
        return self._post("pitra_dosha_report", _birth_body(data, ayanamsha))

    # ── Remedies ───────────────────────────────────────────────────────────────

    def get_gem_suggestion(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Recommended gemstones based on the birth chart."""
        return self._post("basic_gem_suggestion", _birth_body(data, ayanamsha))

    def get_puja_suggestion(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Suggested pujas and rituals for planetary improvement."""
        return self._post("puja_suggestion", _birth_body(data, ayanamsha))

    def get_rudraksha_suggestion(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Rudraksha bead recommendations based on the birth chart."""
        return self._post(
            "rudraksha_suggestion",
            _birth_body(data, ayanamsha),
        )

    def get_sadhesati_remedies(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Remedies to mitigate the effects of Sade Sati."""
        return self._post("sadhesati_remedies", _birth_body(data, ayanamsha))

    # ── Panchang ───────────────────────────────────────────────────────────────

    def get_basic_panchang(self, data: BirthData) -> dict[str, Any]:
        """Basic Panchang: tithi, nakshatra, yoga, karana, vara."""
        return self._post("basic_panchang", data.to_dict())

    def get_advanced_panchang(self, data: BirthData) -> dict[str, Any]:
        """Advanced Panchang including additional timings and planetary positions."""
        return self._post("advanced_panchang", data.to_dict())

    def get_planet_panchang(self, data: BirthData) -> dict[str, Any]:
        """Planetary positions at the time of Panchang calculation."""
        return self._post("planet_panchang", data.to_dict())

    def get_tamil_panchang(self, data: BirthData) -> dict[str, Any]:
        """Tamil Panchang for South Indian traditions."""
        return self._post("tamil_panchang", data.to_dict())

    def get_festival(self, data: BirthData) -> dict[str, Any]:
        """Hindu festivals and auspicious days for the given year/location."""
        return self._post(
            "panchang_festival",
            data.to_dict(),
            body_mode="form",
        )

    # ── Muhurta ────────────────────────────────────────────────────────────────

    def get_hora_muhurta(self, data: BirthData) -> dict[str, Any]:
        """Hora Muhurta — planetary hour timings for the day."""
        return self._post("hora_muhurta", data.to_dict())

    def get_chaughadiya_muhurta(self, data: BirthData) -> dict[str, Any]:
        """Chaughadiya Muhurta — auspicious and inauspicious time blocks."""
        return self._post("chaughadiya_muhurta", data.to_dict())

    # ── Matchmaking ────────────────────────────────────────────────────────────

    def get_match_birth_details(
        self,
        male: BirthData,
        female: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Basic birth details comparison for two individuals."""
        return self._post(
            "match_birth_details",
            _flatten_match_data(male, female, ayanamsha),
        )

    def get_match_obstructions(
        self,
        male: BirthData,
        female: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Compatibility obstructions (Dosha analysis for marriage matching)."""
        return self._post(
            "match_obstructions",
            _flatten_match_data(male, female, ayanamsha),
        )

    def get_match_astro_details(
        self,
        male: BirthData,
        female: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Astrological details for both individuals side by side."""
        return self._post(
            "match_astro_details",
            _flatten_match_data(male, female, ayanamsha),
        )

    def get_match_planet_details(
        self,
        male: BirthData,
        female: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Planetary positions for both individuals."""
        return self._post(
            "match_planet_details",
            _flatten_match_data(male, female, ayanamsha),
        )

    def get_match_manglik_report(
        self,
        male: BirthData,
        female: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Manglik Dosha compatibility report for both individuals."""
        return self._post(
            "match_manglik_report",
            _flatten_match_data(male, female, ayanamsha),
        )

    def get_ashtakoot_points(
        self,
        male: BirthData,
        female: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Ashtakoot Guna Milan points (maximum 36)."""
        return self._post(
            "match_ashtakoot_points",
            _flatten_match_data(male, female, ayanamsha),
        )

    def get_dashakoot_points(
        self,
        male: BirthData,
        female: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Dashakoot compatibility points."""
        return self._post(
            "match_dashakoot_points",
            _flatten_match_data(male, female, ayanamsha),
        )

    def get_match_percentage(
        self,
        male: BirthData,
        female: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Overall compatibility percentage."""
        return self._post(
            "match_percentage",
            _flatten_match_data(male, female, ayanamsha),
        )

    def get_match_report(
        self,
        male: BirthData,
        female: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Consolidated matchmaking summary report."""
        return self._post(
            "match_making_report",
            _flatten_match_data(male, female, ayanamsha),
        )

    def get_detailed_match_report(
        self,
        male: BirthData,
        female: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Comprehensive matchmaking report with detailed analysis."""
        return self._post(
            "match_making_detailed_report",
            _flatten_match_data(male, female, ayanamsha),
        )

    def get_simple_match_report(
        self,
        male: BirthData,
        female: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Simplified matchmaking report for quick compatibility overview."""
        return self._post(
            "match_simple_report",
            _flatten_match_data(male, female, ayanamsha),
        )

    def get_papasamyam(
        self,
        data: BirthData,
        full_name: str,
        ayanamsha: str = DEFAULT_AYANAMSHA,
        date: int | None = None,
    ) -> dict[str, Any]:
        """Single-profile Papasamyam analysis following the live parity contract."""
        return self._post(
            "papasamyam_details",
            _papasamyam_body(data, full_name, ayanamsha, date),
        )

    # ── Varshaphal (Solar Return) ──────────────────────────────────────────────

    def get_varshaphal_details(
        self,
        data: BirthData,
        varshaphal_year: int | None = None,
        year_count: int | None = None,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Varshaphal (annual) chart overview for a given year."""
        return self._post(
            "varshaphal_details",
            _varshaphal_body(data, varshaphal_year, year_count, ayanamsha),
        )

    def get_varshaphal_year_chart(
        self,
        data: BirthData,
        varshaphal_year: int | None = None,
        year_count: int | None = None,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Annual (Varshapal) chart — whole-year divisional chart."""
        return self._post(
            "varshaphal_year_chart",
            _varshaphal_body(data, varshaphal_year, year_count, ayanamsha),
        )

    def get_varshaphal_month_chart(
        self,
        data: BirthData,
        varshaphal_year: int | None = None,
        year_count: int | None = None,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Monthly (Maasa) chart within the Varshaphal year."""
        return self._post(
            "varshaphal_month_chart",
            _varshaphal_body(data, varshaphal_year, year_count, ayanamsha),
        )

    def get_varshaphal_planets(
        self,
        data: BirthData,
        varshaphal_year: int | None = None,
        year_count: int | None = None,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Planetary positions in the Varshaphal chart."""
        return self._post(
            "varshaphal_planets",
            _varshaphal_body(data, varshaphal_year, year_count, ayanamsha),
        )

    def get_varshaphal_muntha(
        self,
        data: BirthData,
        varshaphal_year: int | None = None,
        year_count: int | None = None,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Muntha (annual ascendant) position and significance."""
        return self._post(
            "varshaphal_muntha",
            _varshaphal_body(data, varshaphal_year, year_count, ayanamsha),
        )

    def get_varshaphal_mudda_dasha(
        self,
        data: BirthData,
        varshaphal_year: int | None = None,
        year_count: int | None = None,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Mudda Dasha (annual dasha) running during the Varshaphal year."""
        return self._post(
            "varshaphal_mudda_dasha",
            _varshaphal_body(data, varshaphal_year, year_count, ayanamsha),
        )

    def get_varshaphal_panchavargeeya(
        self,
        data: BirthData,
        varshaphal_year: int | None = None,
        year_count: int | None = None,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Panchavargeeya Bala (five-fold strength) in the Varshaphal."""
        return self._post(
            "varshaphal_panchavargeeya_bala",
            _varshaphal_body(data, varshaphal_year, year_count, ayanamsha),
        )

    def get_varshaphal_harsha_bala(
        self,
        data: BirthData,
        varshaphal_year: int | None = None,
        year_count: int | None = None,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Harsha Bala (strength indicator) in the Varshaphal."""
        return self._post(
            "varshaphal_harsha_bala",
            _varshaphal_body(data, varshaphal_year, year_count, ayanamsha),
        )

    def get_varshaphal_yoga(
        self,
        data: BirthData,
        varshaphal_year: int | None = None,
        year_count: int | None = None,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Yoga formations present in the Varshaphal chart."""
        return self._post(
            "varshaphal_yoga",
            _varshaphal_body(data, varshaphal_year, year_count, ayanamsha),
        )

    def get_varshaphal_saham_points(
        self,
        data: BirthData,
        varshaphal_year: int | None = None,
        year_count: int | None = None,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Saham (Arabic Parts equivalent) positions in the Varshaphal."""
        return self._post(
            "varshaphal_saham_points",
            _varshaphal_body(data, varshaphal_year, year_count, ayanamsha),
        )

    # ── Reports ────────────────────────────────────────────────────────────────

    def get_ascendant_report(
        self,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Interpretive report for the birth ascendant (Lagna)."""
        return self._post("general_ascendant_report", _birth_body(data, ayanamsha))

    def get_nakshatra_report(
        self,
        data: BirthData,
        gender: str = "male",
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Nakshatra (lunar mansion) analysis and characteristics."""
        return self._post(
            "general_nakshatra_report",
            _birth_body(data, ayanamsha, gender=gender),
        )

    def get_house_report(
        self,
        planet: str,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Interpretive report for a planet's house placement."""
        return self._post(
            f"general_house_report/{planet}",
            _birth_body(data, ayanamsha),
        )

    def get_rashi_report(
        self,
        planet: str,
        data: BirthData,
        ayanamsha: str = DEFAULT_AYANAMSHA,
    ) -> dict[str, Any]:
        """Interpretive report for a planet's sign placement."""
        return self._post(
            f"general_rashi_report/{planet}",
            _birth_body(data, ayanamsha),
        )

    # ── Biorhythm ──────────────────────────────────────────────────────────────

    def get_biorhythm(self, data: BirthData) -> dict[str, Any]:
        """Physical, emotional, and intellectual biorhythm cycles."""
        return self._post("biorhythm", data.to_dict())

    def get_moon_biorhythm(self, data: BirthData) -> dict[str, Any]:
        """Lunar biorhythm cycle based on moon phase at birth."""
        return self._post("moon_biorhythm", data.to_dict())
