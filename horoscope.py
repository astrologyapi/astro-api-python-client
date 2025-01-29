import json
from dotenv import load_dotenv
import os
from sdk import AstrologyAPIClient

# Load environment variables from .env file
load_dotenv()

userID = os.getenv('ASTROLOGY_API_USER_ID')
apiKey = os.getenv('ASTROLOGY_API_KEY') 

# Zodiac sign
zodiacName = "taurus"
timezone = 5.5

# Daily Horoscope APIs need to be called
resource = "sun_sign_prediction/daily/"+zodiacName


# instantiate AstrologyAPIClient class
client = AstrologyAPIClient(userID, apiKey)


# call dailyHoroCall method for daily predictions
dailyHoroData = client.dailyHoroCall(resource, zodiacName,timezone)

# print response data recieved from api
print(dailyHoroData)

