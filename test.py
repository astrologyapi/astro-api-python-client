import sdk
import json

userID = "<USER_ID>"
apiKey = "<API_KEY>"

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
client = sdk.AstrologyAPIClient(userID, apiKey)

# call horoscope apis
responseData = client.call(resource, data['date'], data['month'], data['year'], data['hour'], data['minute'], data['latitude'], data['longitude'], data['timezone'])

loaded_json = json.loads(responseData.text)

print(loaded_json)  # <== prints json response.

print(loaded_json['ascendant'])  # <== prints single key