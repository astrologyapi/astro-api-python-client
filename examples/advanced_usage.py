#!/usr/bin/env python3
"""
Advanced usage example for AstrologyAPI SDK.

This demonstrates:
- Asynchronous usage
- PDF generation
- Matchmaking
- Error handling
"""

import asyncio
from astrologyapi import (
    AstrologyAPI,
    AsyncAstrologyAPI,
    BirthData,
    PDFBranding,
)


async def async_example():
    """Example of asynchronous usage."""
    print("=== Async Example ===\n")

    client = AsyncAstrologyAPI("your-api-key")

    try:
        birth = BirthData(
            day=15,
            month=6,
            year=1990,
            hour=10,
            min=30,
            lat=28.61,
            lon=77.20,
            tzone=5.5,
        )

        # Async call to get birth details
        result = await client.vedic.get_birth_details(birth)
        print(f"Birth Details: {result.get('ascendant')}")

        # Async call to get Chinese zodiac
        chinese = await client.chinese.get_zodiac(birth)
        print(f"Chinese Zodiac: {chinese.get('zodiac_sign')}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


def matchmaking_example():
    """Example of matchmaking functionality."""
    print("\n=== Matchmaking Example ===\n")

    client = AstrologyAPI("your-api-key")

    try:
        # Male's birth data
        male = BirthData(
            day=5,
            month=3,
            year=1985,
            hour=14,
            min=30,
            lat=28.61,
            lon=77.20,
            tzone=5.5,
        )

        # Female's birth data
        female = BirthData(
            day=20,
            month=11,
            year=1988,
            hour=9,
            min=15,
            lat=28.61,
            lon=77.20,
            tzone=5.5,
        )

        # Get compatibility percentage
        match = client.vedic.get_match_percentage(male, female)
        print(f"Match Percentage: {match.get('percentage')}%")

        # Get detailed match report
        report = client.vedic.get_detailed_match_report(male, female)
        print(f"Match Report Status: {report.get('status')}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()


def pdf_example():
    """Example of PDF generation."""
    print("\n=== PDF Generation Example ===\n")

    client = AstrologyAPI("your-api-key")

    try:
        birth = BirthData(
            day=15,
            month=6,
            year=1990,
            hour=10,
            min=30,
            lat=28.61,
            lon=77.20,
            tzone=5.5,
        )

        # Optional branding
        branding = PDFBranding(
            company_name="My Astrology",
            company_email="hello@myastrology.com",
            domain_url="https://myastrology.com",
        )

        # Generate mini kundli PDF
        print("Generating Mini Kundli PDF...")
        pdf_content = client.pdf.vedic.get_mini_kundli(
            birth,
            name="John Doe",
            place="Delhi",
            branding=branding,
        )
        print(f"PDF Size: {len(pdf_content)} bytes")

        # Optionally save to file
        with open("mini_kundli.pdf", "wb") as f:
            f.write(pdf_content)
        print("Saved to mini_kundli.pdf")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()


def error_handling_example():
    """Example of error handling."""
    print("\n=== Error Handling Example ===\n")

    client = AstrologyAPI("invalid-api-key")

    try:
        birth = BirthData(
            day=15,
            month=6,
            year=1990,
            hour=10,
            min=30,
            lat=28.61,
            lon=77.20,
            tzone=5.5,
        )

        result = client.vedic.get_birth_details(birth)
        print(result)

    except Exception as e:
        error_name = type(e).__name__
        print(f"Caught {error_name}: {e}")

        if hasattr(e, "status_code"):
            print(f"  Status Code: {e.status_code}")
        if hasattr(e, "data"):
            print(f"  Error Data: {e.data}")
        if hasattr(e, "retry_after"):
            print(f"  Retry After: {e.retry_after} seconds")

    finally:
        client.close()


if __name__ == "__main__":
    # Run sync examples
    matchmaking_example()
    pdf_example()
    error_handling_example()

    # Run async example
    asyncio.run(async_example())
