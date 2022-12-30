import sdk


userID = "<YourUserIdhere>"
apiKey = "<YourApiKeyHere>"

# Zodiac sign
zodiacName = "taurus"
timezone = 5.5

# Daily Horoscope APIs need to be called
resource = "sun_sign_prediction/daily/"+zodiacName


# instantiate AstrologyAPIClient class
client = sdk.AstrologyAPIClient(userID, apiKey)


# call dailyHoroCall method for daily predictions
dailyHoroData = client.dailyHoroCall(resource, zodiacName,timezone)

# print response data recieved from api
print(dailyHoroData)

