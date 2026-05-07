"""
Official Python SDK for AstrologyAPI.com

Provides both sync and async clients with access to:
- Vedic astrology (55+ endpoints)
- Western astrology (30+ endpoints)
- KP astrology (6 endpoints)
- Lal Kitab (5 endpoints)
- Horoscopes (7 endpoints)
- Numerology (18 endpoints)
- Western transits (5 endpoints)
- Tarot (2 endpoints)
- Chinese astrology (2 endpoints)
- PDF reports (8 endpoints)
- Location lookup (2 endpoints)

Example:
    >>> from astrologyapi import AstrologyAPI, BirthData
    >>> client = AstrologyAPI("your-api-key")
    >>> birth = BirthData(
    ...     day=15, month=6, year=1990,
    ...     hour=10, min=30,
    ...     lat=28.61, lon=77.20, tzone=5.5
    ... )
    >>> result = client.vedic.get_birth_details(birth)
    >>> print(result)
"""

from .client import AstrologyAPI, AsyncAstrologyAPI
from .errors import (
    AstrologyAPIError,
    AuthenticationError,
    NetworkError,
    NotFoundError,
    PlanRestrictedError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .models import BirthData, NumeroData, PDFBranding

__version__ = "2.0.0"
__all__ = [
    "AstrologyAPI",
    "AsyncAstrologyAPI",
    "BirthData",
    "NumeroData",
    "PDFBranding",
    "AstrologyAPIError",
    "AuthenticationError",
    "QuotaExceededError",
    "PlanRestrictedError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
]
