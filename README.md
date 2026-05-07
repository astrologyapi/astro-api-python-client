# AstrologyAPI Python SDK

Official Python SDK for [AstrologyAPI.com](https://astrologyapi.com/)

Provides both synchronous and asynchronous clients with full access to:

- **Vedic Astrology** — 55+ endpoints (birth charts, dashas, doshas, matchmaking, etc.)
- **Western Astrology** — 30+ endpoints (natal charts, solar return, synastry, etc.)
- **KP Astrology** — 6 endpoints
- **Lal Kitab** — 5 endpoints
- **Horoscopes** — 7 endpoints (sun-sign and nakshatra predictions)
- **Numerology** — 18 endpoints (Vedic and Western)
- **Western Transits** — 5 endpoints
- **Tarot** — 2 endpoints
- **Chinese Astrology** — 2 endpoints
- **PDF Reports** — 8 endpoints (branded PDF generation)
- **Location** — 2 endpoints (geocoding and timezone lookup)

## Installation

```bash
pip install astrologyapi
```

## Authentication

The SDK uses token-based authentication via the `x-astrologyapi-key` header.

```python
from astrologyapi import AstrologyAPI
client = AstrologyAPI("ak-your-access-token")
```

## Quick Start

### Synchronous Usage

```python
from astrologyapi import AstrologyAPI, BirthData

# Initialize client (using Token-based or Basic auth)
client = AstrologyAPI("ak-your-access-token")

# Define birth data
birth = BirthData(
    day=15,
    month=6,
    year=1990,
    hour=10,
    min=30,
    lat=28.61,      # Latitude
    lon=77.20,      # Longitude
    tzone=5.5       # Timezone
)

# Get Vedic birth details
result = client.vedic.get_birth_details(birth)
print(result)

client.close()
```

### Asynchronous Usage

```python
import asyncio
from astrologyapi import AsyncAstrologyAPI, BirthData

async def main():
    # Initialize client (using Token-based or Basic auth)
    client = AsyncAstrologyAPI("ak-your-access-token")

    birth = BirthData(
        day=15, month=6, year=1990,
        hour=10, min=30,
        lat=28.61, lon=77.20, tzone=5.5
    )

    result = await client.vedic.get_birth_details(birth)
    print(result)

    await client.close()

asyncio.run(main())
```

### Environment Variables

You can also use environment variables to configure the client:

```bash
export ASTROLOGYAPI_API_KEY="ak-your-token"
```

```python
from astrologyapi import AstrologyAPI

# Automatically picks up the env var
client = AstrologyAPI.from_env()
```

## Features

### Full Type Hints

All methods are fully typed for IDE autocomplete and type checking.

```python
def get_birth_details(self, data: BirthData) -> dict[str, Any]: ...
```

### Typed Error Handling

Specific error classes for different scenarios:

```python
from astrologyapi import (
    AuthenticationError,
    QuotaExceededError,
    ValidationError,
    RateLimitError,
    NetworkError,
)

try:
    result = client.vedic.get_birth_details(birth)
except AuthenticationError as e:
    print(f"Invalid API key: {e}")
except QuotaExceededError as e:
    print(f"API quota exceeded: {e}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
```

### PDF Generation

Generate branded PDF reports:

```python
from astrologyapi import PDFBranding

branding = PDFBranding(
    company_name="My Astrology",
    company_email="hello@myastrology.com",
    domain_url="https://myastrology.com"
)

pdf_bytes = client.pdf.vedic.get_mini_kundli(
    birth,
    name="John Doe",
    place="Delhi",
    branding=branding
)

# Save to file
with open("kundli.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### Matchmaking

Compare two birth charts for compatibility:

```python
male = BirthData(day=5, month=3, year=1985, hour=14, min=30, lat=28.61, lon=77.20, tzone=5.5)
female = BirthData(day=20, month=11, year=1988, hour=9, min=15, lat=28.61, lon=77.20, tzone=5.5)

compatibility = client.vedic.get_match_percentage(male, female)
print(f"Match: {compatibility['percentage']}%")

detailed_report = client.vedic.get_detailed_match_report(male, female)
```

### Location Lookup

Resolve place names to coordinates:

```python
locations = client.location.get_geo_details("Mumbai")
for loc in locations:
    print(f"{loc['name']}: {loc['latitude']}, {loc['longitude']}")

timezone = client.location.get_timezone(
    day=15, month=6, year=1990,
    hour=10, min=30,
    lat=28.61, lon=77.20
)
print(f"Timezone: {timezone['tzone']}")
```

## Examples

See the `examples/` directory for more detailed examples:

- `basic_usage.py` — Basic synchronous usage
- `advanced_usage.py` — Async, matchmaking, PDFs, error handling

## API Documentation

Full API documentation is available at [docs.astrologyapi.com](https://docs.astrologyapi.com/)

## Retry Logic

The SDK automatically retries on transient errors with exponential backoff:
- Max 3 retries (configurable)
- Backoff: 1s, 2s, 4s
- Network errors and timeouts are retried
- Rate limit errors (429) include `retry_after` hint

## Thread Safety

- `AstrologyAPI` (sync) is not thread-safe; create separate instances per thread
- `AsyncAstrologyAPI` should be used with async context managers

## Python Version

Requires Python 3.9 or higher.

## License

MIT License. See LICENSE file for details.

## Support

For issues or questions:
- GitHub: https://github.com/astrologyapi/astro-api-python-client
- Email: support@astrologyapi.com
- Docs: https://docs.astrologyapi.com/
