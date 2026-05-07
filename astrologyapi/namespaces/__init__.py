"""
Namespace modules for AstrologyAPI SDK.
"""

from .chinese import ChineseNamespace
from .horoscopes import HoroscopesNamespace
from .kp import KPNamespace
from .lal_kitab import LalKitabNamespace
from .location import LocationNamespace
from .numerology import NumerologyNamespace
from .pdf import PDFNamespace
from .tarot import TarotNamespace
from .vedic import VedicNamespace
from .western import WesternNamespace
from .western_transit import WesternTransitNamespace

__all__ = [
    "ChineseNamespace",
    "HoroscopesNamespace",
    "KPNamespace",
    "LalKitabNamespace",
    "LocationNamespace",
    "NumerologyNamespace",
    "PDFNamespace",
    "TarotNamespace",
    "VedicNamespace",
    "WesternNamespace",
    "WesternTransitNamespace",
]
