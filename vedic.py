import json
from dotenv import load_dotenv
import os
from sdk import AstrologyAPIClient

# Load environment variables from .env file
load_dotenv()

userID = os.getenv('ASTROLOGY_API_USER_ID') 
apiKey = os.getenv('ASTROLOGY_API_KEY') 



# Instantiate the client
client = AstrologyAPIClient(userID, apiKey)

# Example 1: Natal Wheel Chart API (JSON)
horoscope_data = {
    'day': 10,
    'month': 12,
    'year': 1993,
    'hour': 1,
    'min': 25,
    'lat': 25,
    'lon': 82,
    'tzone': 5.5
}
resource = "birth_details"
response = client.customCall(
    resource,
    horoscope_data
)
print("Vedic Response:")
print(json.dumps(response, indent=4))