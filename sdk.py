import requests


class VRClient:
    baseURL = "http://api.vedicrishiastro.com/v1/"

    def __init__(self, uid, key):
        self.userID = uid
        self.apiKey = key

    def getUrl(cls):
        return cls.baseURL

    def getResponse(self, resource, data):
        # print(self.userID)
        url = self.getUrl() + resource
        resp = requests.post(url, data=data, auth=(self.userID, self.apiKey))
        return resp

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
        tempData = dict(mData.items() + fData.items())
        return tempData

    def call(self, resource, date, month, year, hour, minute, latitude, longitude, timezone):
        data = self.packageHoroData(date, month, year, hour, minute, latitude, longitude, timezone)
        return self.getResponse(resource, data)

    def matchMakingCall(self, resource, maleBirthData, femaleBirthData):
        data = self.packageMatchMakingData(maleBirthData, femaleBirthData)
        return self.getResponse(resource, data)

    def numeroCall(self, resource, date, month, year, name):
        data = self.packageNumeroData(date, month, year, name)
        return self.getResponse(resource, data)
