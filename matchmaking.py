import json
from dotenv import load_dotenv
import os
from sdk import AstrologyAPIClient

# Load environment variables from .env file
load_dotenv()

userID = os.getenv('ASTROLOGY_API_USER_ID')
apiKey = os.getenv('ASTROLOGY_API_KEY') 

# create a male profile data
maleData = {
    'date': 25,
    'month': 12,
    'year': 1988,
    'hour': 4,
    'minute': 0,
    'latitude': 25.123,
    'longitude': 82.34,
    'timezone': 5.5
}
# create female data
femaleData = {
    'date': 27,
    'month': 1,
    'year': 1990,
    'hour': 13,
    'minute': 36,
    'latitude': 25.123,
    'longitude': 82.34,
    'timezone': 5.5
}

# match making api to be called
resource = "match_ashtakoot_points"

# create instance of AstrologyAPIClient

client = AstrologyAPIClient(userID, apiKey)

# call matchMakingCall method of AstrologyAPIClient for matching apis
matchMakingData = client.matchMakingCall(resource, maleData, femaleData)

# print response data recieved from api
print(matchMakingData)

