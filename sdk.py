import requests

class AstrologyAPIClient:
    baseURL = "https://json.astrologyapi.com/v1/"
    basePDFURL = "https://pdf.astrologyapi.com/v1/"

    def __init__(self, uid, key):
        self.userID = uid
        self.apiKey = key

    def getBaseURL(self, apiType="json"):
        """Determine the base URL based on the API type."""
        if apiType.lower() == "pdf":
            return self.basePDFURL
        return self.baseURL

    def getResponse(self, resource, data, headers=None, apiType="json"):
        """Make the API request and return the JSON response."""
        headers = headers or {}
        base_url = self.getBaseURL(apiType)
        url = base_url + resource

        try:
            response = requests.post(
                url,
                data=data,
                auth=(self.userID, self.apiKey),
                headers=headers
            )
            response.raise_for_status()  # Raise an error for bad status codes
            return response.json()  # Parse and return JSON response
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - {response.text}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
        except ValueError as json_err:
            print(f"JSON decoding failed: {json_err}")
        return None  # Return None if any exception occurs

    def packageHoroData(self, date, month, year, hour, minute, latitude, longitude, timezone):
        return {
            'day': date,
            'month': month,
            'year': year,
            'hour': hour,
            'min': minute,
            'lat': latitude,
            'lon': longitude,
            'tzone': timezone
        }

    def packageDailyHoroData(self, zodiacName, timezone):
        return {
            'zodiacName': zodiacName,
            'timezone': timezone,
        }

    def packageNumeroData(self, date, month, year, name):
        return {
            'day': date,
            'month': month,
            'year': year,
            'name': name
        }

    def packageMatchMakingData(self, maleBirthData, femaleBirthData):
        mData = {
            'm_day': maleBirthData['date'],
            'm_month': maleBirthData['month'],
            'm_year': maleBirthData['year'],
            'm_hour': maleBirthData['hour'],
            'm_min': maleBirthData['minute'],
            'm_lat': maleBirthData['latitude'],
            'm_lon': maleBirthData['longitude'],
            'm_tzone': maleBirthData['timezone']
        }

        fData = {
            'f_day': femaleBirthData['date'],
            'f_month': femaleBirthData['month'],
            'f_year': femaleBirthData['year'],
            'f_hour': femaleBirthData['hour'],
            'f_min': femaleBirthData['minute'],
            'f_lat': femaleBirthData['latitude'],
            'f_lon': femaleBirthData['longitude'],
            'f_tzone': femaleBirthData['timezone']
        }

        return {**mData, **fData}

    def call(self, resource, date, month, year, hour, minute, latitude, longitude, timezone, apiType="json"):
        data = self.packageHoroData(date, month, year, hour, minute, latitude, longitude, timezone)
        return self.getResponse(resource, data, apiType=apiType)

    def matchMakingCall(self, resource, maleBirthData, femaleBirthData, apiType="json"):
        data = self.packageMatchMakingData(maleBirthData, femaleBirthData)
        return self.getResponse(resource, data, apiType=apiType)

    def numeroCall(self, resource, date, month, year, name, apiType="json"):
        data = self.packageNumeroData(date, month, year, name)
        return self.getResponse(resource, data, apiType=apiType)

    def dailyHoroCall(self, resource, zodiacName, timezone, apiType="json"):
        data = self.packageDailyHoroData(zodiacName, timezone)
        return self.getResponse(resource, data, apiType=apiType)

    def customCall(self, resource, data, headers=None, apiType="json"):
        return self.getResponse(resource, data, headers=headers, apiType=apiType)

    def callPDF(self, resource, data, headers=None):
        """Convenience method for PDF API calls."""
        return self.getResponse(resource, data, headers=headers, apiType="pdf")
