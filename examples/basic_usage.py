#!/usr/bin/env python3
"""
Basic usage example for AstrologyAPI SDK.

This demonstrates synchronous usage of the SDK.
"""

from astrologyapi import AstrologyAPI, BirthData

# Initialize the client
# You can pass the API key directly or use the ASTROLOGYAPI_API_KEY env var
client = AstrologyAPI("your-api-key")

# Define birth data
birth = BirthData(
    day=15,
    month=6,
    year=1990,
    hour=10,
    min=30,
    lat=28.61,        # Latitude (Delhi)
    lon=77.20,        # Longitude (Delhi)
    tzone=5.5,        # Timezone (IST)
)

try:
    # Get Vedic birth details
    print("Vedic Birth Details:")
    result = client.vedic.get_birth_details(birth)
    print(f"  Ascendant: {result.get('ascendant')}")
    print(f"  Sun Sign: {result.get('sun_sign')}")
    print(f"  Moon Sign: {result.get('moon_sign')}")
    print()

    # Get planets
    print("Planetary Positions:")
    planets = client.vedic.get_planets(birth)
    if "planets" in planets:
        for planet in planets["planets"][:3]:  # Show first 3 planets
            print(f"  {planet.get('name')}: {planet.get('sign')} {planet.get('degree')}")
    print()

    # Get Western horoscope
    print("Western Horoscope:")
    western = client.western.get_horoscope(birth)
    print(f"  Western Ascendant: {western.get('ascendant')}")
    print()

    # Get location details
    print("Location Lookup:")
    locations = client.location.get_geo_details("Mumbai")
    if locations:
        loc = locations[0]
        print(f"  Place: {loc.get('name')}")
        print(f"  Latitude: {loc.get('latitude')}")
        print(f"  Longitude: {loc.get('longitude')}")
    print()

    # Get sun-sign horoscope
    print("Sun-Sign Daily Horoscope (Gemini):")
    horoscope = client.horoscopes.get_daily("gemini")
    print(f"  Prediction: {horoscope.get('prediction', 'N/A')[:100]}...")
    print()

    # Get numerology
    from astrologyapi import NumeroData
    numero = NumeroData(day=15, month=6, year=1990, name="John Doe")
    print("Numerology:")
    num_result = client.numerology.get_table(numero)
    if "psychic_number" in num_result:
        print(f"  Psychic Number: {num_result['psychic_number']}")
    print()

    # Get tarot reading
    print("Tarot Reading:")
    tarot = client.tarot.get_predictions()
    print(f"  Prediction: {tarot.get('prediction', 'N/A')[:100]}...")

except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, "status_code"):
        print(f"Status: {e.status_code}")
    if hasattr(e, "data"):
        print(f"Data: {e.data}")

finally:
    client.close()
