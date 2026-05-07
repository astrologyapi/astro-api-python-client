"""
Data models for AstrologyAPI SDK.

Provides dataclasses for common input/output structures:
- BirthData: Core birth chart input
- NumeroData: Numerology-specific input
- PDFBranding: Optional PDF report branding
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, fields
from typing import Any


@dataclass
class BirthData:
    """
    Core birth chart data.

    Attributes:
        day: Day of birth (1-31)
        month: Month of birth (1-12)
        year: Year of birth (4-digit)
        hour: Hour of birth (0-23)
        min: Minute of birth (0-59)
        lat: Latitude (-90.0 to 90.0)
        lon: Longitude (-180.0 to 180.0)
        tzone: Timezone offset in hours (e.g., 5.5 for IST, -5.0 for EST)
        name: Full name of the individual (optional)
    """

    day: int
    month: int
    year: int
    hour: int
    min: int
    lat: float
    lon: float
    tzone: float
    name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, omitting None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class NumeroData:
    """
    Numerology-specific birth data.

    Attributes:
        day: Day of birth (1-31)
        month: Month of birth (1-12)
        year: Year of birth (4-digit)
        name: Full name (optional, used for name-based numerology)
    """

    day: int
    month: int
    year: int
    name: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with snake_case keys matching API."""
        data = asdict(self)
        # Remove empty name if not provided
        if not self.name:
            del data["name"]
        return data


@dataclass
class PDFBranding:
    """
    Optional branding fields for PDF reports.

    All fields are optional — only provided values are sent to the API.

    Attributes:
        logo_url: URL to company logo image
        company_name: Name of your company/brand
        company_info: Brief company description
        domain_url: Website URL for branding
        company_email: Contact email address
        company_landline: Landline phone number
        company_mobile: Mobile phone number
        footer_link: URL for PDF footer link
        chart_style: Chart style preference (if API supports this)
    """

    logo_url: str | None = None
    company_name: str | None = None
    company_info: str | None = None
    domain_url: str | None = None
    company_email: str | None = None
    company_landline: str | None = None
    company_mobile: str | None = None
    footer_link: str | None = None
    chart_style: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary, omitting None values.
        Keys are converted to snake_case matching API expectations.
        """
        result = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                result[field.name] = value
        return result
