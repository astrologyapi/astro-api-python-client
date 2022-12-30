# Astrology-API-Python-Client

This is Python client to consume Astrology APIs

# Where to get API Key

You can visit https://www.astrologyapi.com/ to get the astrology API key to be used for your websites or
mobile applications.

# How to Use

1. Copy sdk.py class file to your local or server file system
2. Instantiate `AstrologyAPIClient` class as follows -

   ```
   clientInstance = AstrologyAPIClient(userID, apiKey)
   ```

   Replace `userID` and ` apiKey` with your id and keys respectively.
   You can get the API key details from https://www.astrologyapi.com/

3. Call the api

   ```
   response = clientInstance.call(apiName, date, month, year, hour, min, lat, lon, tzone)

   ```

   View test.py for more details about calling APIs.

4. The `response` will be a JSON encoded data returned as an API response. Eg. for `/planets/` api -
   ```
   [
       {
           "id":0,
           "name":"SUN",
           "fullDegree":95.83230788313479,
           "normDegree":5.8323078831347885,"speed":0.9547191489638442,
           "isRetro":"false",
           "sign":"CANCER",
           "signLord":"MOON",
           "nakshatra":"PUSHYA",
           "nakshatraLord":7,
           "house":11
       }
       ...
   ]
   ```
5. For calling numerological api, call method name `numeroCall()` as follows -

   ```
       response = clientInstance.numeroCall(apiName, date, month, year, name)

   ```

   Only date, month and year along with name is required for numerological calculations.
   Run the numerology.py file to test numerological APIs.

6. For match making horoscope calculations and report analysis, please use `matchMakingCall()` method as follows -

   ````
           response = clientInstance.matchMakingCall(resource, maleBirthData, femaleBirthData)

   		/where  maleBirthData and femaleBirthData is mapped as follows -

   		                    femaleData = {

   		                        'date': 9,
   		                        'month': 12,
   		                        'year': 1990,
   		                        'hour': 12,
   		                        'minute': 56,
   		                        'latitude': 25.123,
   		                        'longitude': 82.34,
   		                        'timezone': 5.5
   		                    }

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
   		    ```
   		Run matchmaking.py file to run AstrologyAPI Match Making APIs.
   		For API documentation, visit - https://www.astrologyapi.com/docs/

   ````
