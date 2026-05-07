"""
PDF namespace.

Generate branded PDF astrology reports.
PDF endpoints may return raw PDF bytes or a successful JSON body containing
`pdf_url`, so these helpers return the parsed runtime payload as-is.
"""

from __future__ import annotations

from typing import Any

from ..models import BirthData, PDFBranding


def _flatten_branding(branding: PDFBranding | None) -> dict[str, Any]:
    """Flatten PDF branding fields while normalizing chart-style casing."""
    if not branding:
        return {}

    payload = branding.to_dict()
    chart_style = payload.get("chart_style")
    if isinstance(chart_style, str):
        payload["chart_style"] = chart_style.upper()
    return payload


def _split_name(name: str | None) -> tuple[str, str]:
    """Split a full name into first and last segments."""
    if not name:
        return "", ""
    parts = name.strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _vedic_single_pdf_body(
    data: BirthData,
    *,
    name: str | None,
    gender: str,
    place: str | None,
    language: str,
    branding: PDFBranding | None,
) -> dict[str, Any]:
    """Build the Vedic PDF request body that matches the Postman contract."""
    body = {
        "name": name if name is not None else data.name,
        "day": data.day,
        "month": data.month,
        "year": data.year,
        "hour": data.hour,
        "min": data.min,
        "lat": data.lat,
        "lon": data.lon,
        "tzone": data.tzone,
        "gender": gender,
        "language": language,
        "place": place,
    }
    body.update(_flatten_branding(branding))
    return body


def _western_single_pdf_body(
    data: BirthData,
    *,
    name: str | None,
    place: str | None,
    language: str,
    branding: PDFBranding | None,
    solar_year: int | None = None,
) -> dict[str, Any]:
    """Build the Western single-profile PDF body expected by Postman."""
    body = {
        "name": name,
        "day": data.day,
        "month": data.month,
        "year": data.year,
        "hour": data.hour,
        "minute": data.min,
        "latitude": data.lat,
        "longitude": data.lon,
        "timezone": data.tzone,
        "place": place,
        "language": language,
    }
    if solar_year is not None:
        body["solar_year"] = solar_year
    body.update(_flatten_branding(branding))
    return body


def _vedic_match_pdf_body(
    male: BirthData,
    female: BirthData,
    *,
    name: str | None,
    partner_name: str | None,
    place: str | None,
    partner_place: str | None,
    language: str,
    branding: PDFBranding | None,
    ashtakoot: bool,
    papasyam: bool,
    dashakoot: bool,
) -> dict[str, Any]:
    """Build the Vedic match-making PDF request body."""
    male_first, male_last = _split_name(name)
    female_first, female_last = _split_name(partner_name)
    resolved_partner_place = partner_place if partner_place is not None else place

    body = {
        "name": name,
        "partner_name": partner_name,
        "m_first_name": male_first,
        "m_last_name": male_last,
        "m_day": male.day,
        "m_month": male.month,
        "m_year": male.year,
        "m_hour": male.hour,
        "m_minute": male.min,
        "m_latitude": male.lat,
        "m_longitude": male.lon,
        "m_timezone": male.tzone,
        "m_place": place,
        "f_first_name": female_first,
        "f_last_name": female_last,
        "f_day": female.day,
        "f_month": female.month,
        "f_year": female.year,
        "f_hour": female.hour,
        "f_minute": female.min,
        "f_latitude": female.lat,
        "f_longitude": female.lon,
        "f_timezone": female.tzone,
        "f_place": resolved_partner_place,
        "language": language,
        "ashtakoot": ashtakoot,
        "papasyam": papasyam,
        "dashakoot": dashakoot,
    }
    body.update(_flatten_branding(branding))
    return body


def _western_synastry_pdf_body(
    person1: BirthData,
    person2: BirthData,
    *,
    name: str | None,
    partner_name: str | None,
    place: str | None,
    partner_place: str | None,
    language: str,
    branding: PDFBranding | None,
) -> dict[str, Any]:
    """Build the Western synastry PDF request body."""
    first_name, last_name = _split_name(name)
    partner_first, partner_last = _split_name(partner_name)
    resolved_partner_place = partner_place if partner_place is not None else place

    body = {
        "name": name,
        "partner_name": partner_name,
        "p_first_name": first_name,
        "p_last_name": last_name,
        "p_day": person1.day,
        "p_month": person1.month,
        "p_year": person1.year,
        "p_hour": person1.hour,
        "p_minute": person1.min,
        "p_latitude": person1.lat,
        "p_longitude": person1.lon,
        "p_timezone": person1.tzone,
        "p_place": place,
        "s_first_name": partner_first,
        "s_last_name": partner_last,
        "s_day": person2.day,
        "s_month": person2.month,
        "s_year": person2.year,
        "s_hour": person2.hour,
        "s_minute": person2.min,
        "s_latitude": person2.lat,
        "s_longitude": person2.lon,
        "s_timezone": person2.tzone,
        "s_place": resolved_partner_place,
        "language": language,
    }
    body.update(_flatten_branding(branding))
    return body


class VedicPDF:
    """Vedic PDF report endpoints."""

    def __init__(self, http_client: Any) -> None:
        self.http = http_client

    def _post_binary(self, endpoint: str, body: dict[str, Any]) -> Any:
        return self.http.post_binary(endpoint, body, body_mode="form")

    def get_mini_kundli(
        self,
        data: BirthData,
        name: str | None = None,
        place: str | None = None,
        branding: PDFBranding | None = None,
        *,
        gender: str = "male",
        language: str = "en",
    ) -> Any:
        """
        Mini Kundli PDF — compact birth chart summary (1–2 pages).
        """
        body = _vedic_single_pdf_body(
            data,
            name=name,
            gender=gender,
            place=place,
            language=language,
            branding=branding,
        )
        return self._post_binary("mini_horoscope_pdf", body)

    def get_basic_horoscope(
        self,
        data: BirthData,
        name: str | None = None,
        place: str | None = None,
        branding: PDFBranding | None = None,
        *,
        gender: str = "male",
        language: str = "en",
    ) -> Any:
        """
        Basic horoscope PDF — standard birth chart with planetary positions and dasha table.
        """
        body = _vedic_single_pdf_body(
            data,
            name=name,
            gender=gender,
            place=place,
            language=language,
            branding=branding,
        )
        return self._post_binary("basic_horoscope_pdf", body)

    def get_professional_horoscope(
        self,
        data: BirthData,
        name: str | None = None,
        place: str | None = None,
        branding: PDFBranding | None = None,
        *,
        gender: str = "male",
        language: str = "en",
    ) -> Any:
        """
        Professional horoscope PDF — comprehensive report with charts, dashas, doshas, and interpretations.
        """
        body = _vedic_single_pdf_body(
            data,
            name=name,
            gender=gender,
            place=place,
            language=language,
            branding=branding,
        )
        return self._post_binary("pro_horoscope_pdf", body)

    def get_match_making(
        self,
        male: BirthData,
        female: BirthData,
        name: str | None = None,
        partner_name: str | None = None,
        place: str | None = None,
        branding: PDFBranding | None = None,
        *,
        partner_place: str | None = None,
        language: str = "en",
        ashtakoot: bool = True,
        papasyam: bool = True,
        dashakoot: bool = True,
    ) -> Any:
        """Match Making PDF — compatibility report for two individuals."""
        body = _vedic_match_pdf_body(
            male,
            female,
            name=name,
            partner_name=partner_name,
            place=place,
            partner_place=partner_place,
            language=language,
            branding=branding,
            ashtakoot=ashtakoot,
            papasyam=papasyam,
            dashakoot=dashakoot,
        )
        return self._post_binary("match_making_pdf", body)


class WesternPDF:
    """Western PDF report endpoints."""

    def __init__(self, http_client: Any) -> None:
        self.http = http_client

    def _post_binary(self, endpoint: str, body: dict[str, Any]) -> Any:
        return self.http.post_binary(endpoint, body, body_mode="form")

    def get_natal_chart(
        self,
        data: BirthData,
        name: str | None = None,
        place: str | None = None,
        branding: PDFBranding | None = None,
        *,
        language: str = "en",
    ) -> Any:
        """Western natal chart PDF — birth chart with aspects, house positions, and interpretation."""
        body = _western_single_pdf_body(
            data,
            name=name,
            place=place,
            language=language,
            branding=branding,
        )
        return self._post_binary("natal_horoscope_report/tropical", body)

    def get_life_forecast(
        self,
        data: BirthData,
        name: str | None = None,
        place: str | None = None,
        branding: PDFBranding | None = None,
        *,
        language: str = "en",
    ) -> Any:
        """Life forecast PDF — transit-based annual forecast report."""
        body = _western_single_pdf_body(
            data,
            name=name,
            place=place,
            language=language,
            branding=branding,
        )
        return self._post_binary("life_forecast_report/tropical", body)

    def get_solar_return(
        self,
        data: BirthData,
        name: str | None = None,
        place: str | None = None,
        branding: PDFBranding | None = None,
        *,
        language: str = "en",
        solar_year: int | None = None,
    ) -> Any:
        """Solar Return PDF — annual solar return chart and interpretation."""
        body = _western_single_pdf_body(
            data,
            name=name,
            place=place,
            language=language,
            branding=branding,
            solar_year=solar_year,
        )
        return self._post_binary("solar_return_report/tropical", body)

    def get_synastry(
        self,
        person1: BirthData,
        person2: BirthData,
        name: str | None = None,
        partner_name: str | None = None,
        place: str | None = None,
        branding: PDFBranding | None = None,
        *,
        partner_place: str | None = None,
        language: str = "en",
    ) -> Any:
        """Synastry couple PDF — relationship compatibility report for two people."""
        body = _western_synastry_pdf_body(
            person1,
            person2,
            name=name,
            partner_name=partner_name,
            place=place,
            partner_place=partner_place,
            language=language,
            branding=branding,
        )
        return self._post_binary("synastry_couple_report/tropical", body)


class PDFNamespace:
    """PDF namespace with vedic and western sub-namespaces."""

    vedic: VedicPDF
    western: WesternPDF

    def __init__(self, http_client: Any) -> None:
        self.vedic = VedicPDF(http_client)
        self.western = WesternPDF(http_client)
