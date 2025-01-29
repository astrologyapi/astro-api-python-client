from dotenv import load_dotenv
import os
from sdk import AstrologyAPIClient
import json


# Load environment variables from .env file
load_dotenv()

userID = os.getenv('ASTROLOGY_API_USER_ID')
apiKey = os.getenv('ASTROLOGY_API_KEY') 

# make some dummy data in order to call astrology api
data = {
    'date': 10,
    'month': 12,
    'year': 1993,
    'hour': 1,
    'minute': 25,
    'latitude': 25,
    'longitude': 82,
    'timezone': 5.5
}

# api name which is to be called
resource = "astro_details"

# instantiate AstrologyAPIClient class
client = AstrologyAPIClient(userID, apiKey)

# call horoscope apis
responseData = client.call(resource, data['date'], data['month'], data['year'], data['hour'], data['minute'], data['latitude'], data['longitude'], data['timezone'])


print(responseData)  # <== prints json response.

#prints a single key
print(responseData['ascendant'])
