"""
Main AstrologyAPI client.

Provides both sync (AstrologyAPI) and async (AsyncAstrologyAPI) clients
with access to all 11 astrology namespaces.
"""

import os
from functools import cached_property
from typing import Any

from ._http import AsyncHttpClient, HttpClient
from .namespaces import (
    ChineseNamespace,
    HoroscopesNamespace,
    KPNamespace,
    LalKitabNamespace,
    LocationNamespace,
    NumerologyNamespace,
    PDFNamespace,
    TarotNamespace,
    VedicNamespace,
    WesternNamespace,
    WesternTransitNamespace,
)


class AstrologyAPI:
    """
    Synchronous client for AstrologyAPI.

    Provides access to all 11 astrology namespaces via cached properties.

    Example:
        >>> from astrologyapi import AstrologyAPI, BirthData
        >>> client = AstrologyAPI("your-api-key")
        >>> birth = BirthData(
        ...     day=15, month=6, year=1990,
        ...     hour=10, min=30,
        ...     lat=28.61, lon=77.20, tzone=5.5
        ... )
        >>> result = client.vedic.get_birth_details(birth)
    """

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = 30.0,
        retries: int = 3,
    ) -> None:
        """
        Initialize the sync AstrologyAPI client.

        Args:
            api_key: Your AstrologyAPI API key. Can also be set via ASTROLOGYAPI_API_KEY env var.
            timeout: Request timeout in seconds (default: 30.0)
            retries: Number of retry attempts for transient errors (default: 3)
        """
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self._http = HttpClient(api_key, timeout=timeout, retries=retries)

    @classmethod
    def from_env(cls) -> "AstrologyAPI":
        """
        Create a client using the ASTROLOGYAPI_API_KEY environment variable.

        Returns:
            AstrologyAPI client

        Raises:
            ValueError: If ASTROLOGYAPI_API_KEY is not set
        """
        api_key = os.getenv("ASTROLOGYAPI_API_KEY")
        if not api_key:
            raise ValueError(
                "ASTROLOGYAPI_API_KEY environment variable not set. "
                "Please set your API key or pass it to AstrologyAPI(api_key=...)"
            )
        return cls(api_key)

    def close(self) -> None:
        """Close the underlying HTTP client connection."""
        self._http.close()

    def __enter__(self) -> "AstrologyAPI":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ── Namespaces ─────────────────────────────────────────────────────────────

    @cached_property
    def vedic(self) -> VedicNamespace:
        """Vedic astrology namespace."""
        return VedicNamespace(self._http)

    @cached_property
    def western(self) -> WesternNamespace:
        """Western (tropical) astrology namespace."""
        return WesternNamespace(self._http)

    @cached_property
    def kp(self) -> KPNamespace:
        """KP (Krishnamurti Paddhati) astrology namespace."""
        return KPNamespace(self._http)

    @cached_property
    def lal_kitab(self) -> LalKitabNamespace:
        """Lal Kitab astrology namespace."""
        return LalKitabNamespace(self._http)

    @cached_property
    def horoscopes(self) -> HoroscopesNamespace:
        """Horoscopes (sun-sign and nakshatra) namespace."""
        return HoroscopesNamespace(self._http)

    @cached_property
    def numerology(self) -> NumerologyNamespace:
        """Numerology (Vedic and Western) namespace."""
        return NumerologyNamespace(self._http)

    @cached_property
    def western_transit(self) -> WesternTransitNamespace:
        """Western transit namespace."""
        return WesternTransitNamespace(self._http)

    @cached_property
    def tarot(self) -> TarotNamespace:
        """Tarot namespace."""
        return TarotNamespace(self._http)

    @cached_property
    def chinese(self) -> ChineseNamespace:
        """Chinese astrology namespace."""
        return ChineseNamespace(self._http)

    @cached_property
    def pdf(self) -> PDFNamespace:
        """PDF reports namespace (vedic and western)."""
        return PDFNamespace(self._http)

    @cached_property
    def location(self) -> LocationNamespace:
        """Location and timezone namespace."""
        return LocationNamespace(self._http)


class AsyncAstrologyAPI:
    """
    Asynchronous client for AstrologyAPI.

    Provides the same interface as AstrologyAPI but with async/await.
    All namespace methods are coroutines.

    Example:
        >>> import asyncio
        >>> from astrologyapi import AsyncAstrologyAPI, BirthData
        >>> async def main():
        ...     client = AsyncAstrologyAPI("your-api-key")
        ...     birth = BirthData(
        ...         day=15, month=6, year=1990,
        ...         hour=10, min=30,
        ...         lat=28.61, lon=77.20, tzone=5.5
        ...     )
        ...     result = await client.vedic.get_birth_details(birth)
        ...     print(result)
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = 30.0,
        retries: int = 3,
    ) -> None:
        """
        Initialize the async AstrologyAPI client.

        Args:
            api_key: Your AstrologyAPI API key. Can also be set via ASTROLOGYAPI_API_KEY env var.
            timeout: Request timeout in seconds (default: 30.0)
            retries: Number of retry attempts for transient errors (default: 3)
        """
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self._http = AsyncHttpClient(api_key, timeout=timeout, retries=retries)

    @classmethod
    def from_env(cls) -> "AsyncAstrologyAPI":
        """
        Create a client using the ASTROLOGYAPI_API_KEY environment variable.

        Returns:
            AsyncAstrologyAPI client

        Raises:
            ValueError: If ASTROLOGYAPI_API_KEY is not set
        """
        api_key = os.getenv("ASTROLOGYAPI_API_KEY")
        if not api_key:
            raise ValueError(
                "ASTROLOGYAPI_API_KEY environment variable not set. "
                "Please set your API key or pass it to AsyncAstrologyAPI(api_key=...)"
            )
        return cls(api_key)

    async def close(self) -> None:
        """Close the underlying HTTP client connection."""
        await self._http.close()

    async def __aenter__(self) -> "AsyncAstrologyAPI":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    # ── Namespaces ─────────────────────────────────────────────────────────────

    @cached_property
    def vedic(self) -> VedicNamespace:
        """Vedic astrology namespace."""
        return VedicNamespace(self._http)

    @cached_property
    def western(self) -> WesternNamespace:
        """Western (tropical) astrology namespace."""
        return WesternNamespace(self._http)

    @cached_property
    def kp(self) -> KPNamespace:
        """KP (Krishnamurti Paddhati) astrology namespace."""
        return KPNamespace(self._http)

    @cached_property
    def lal_kitab(self) -> LalKitabNamespace:
        """Lal Kitab astrology namespace."""
        return LalKitabNamespace(self._http)

    @cached_property
    def horoscopes(self) -> HoroscopesNamespace:
        """Horoscopes (sun-sign and nakshatra) namespace."""
        return HoroscopesNamespace(self._http)

    @cached_property
    def numerology(self) -> NumerologyNamespace:
        """Numerology (Vedic and Western) namespace."""
        return NumerologyNamespace(self._http)

    @cached_property
    def western_transit(self) -> WesternTransitNamespace:
        """Western transit namespace."""
        return WesternTransitNamespace(self._http)

    @cached_property
    def tarot(self) -> TarotNamespace:
        """Tarot namespace."""
        return TarotNamespace(self._http)

    @cached_property
    def chinese(self) -> ChineseNamespace:
        """Chinese astrology namespace."""
        return ChineseNamespace(self._http)

    @cached_property
    def pdf(self) -> PDFNamespace:
        """PDF reports namespace (vedic and western)."""
        return PDFNamespace(self._http)

    @cached_property
    def location(self) -> LocationNamespace:
        """Location and timezone namespace."""
        return LocationNamespace(self._http)
