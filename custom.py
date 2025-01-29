
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

# Example 1: Horoscope API (JSON)
horoscope_data = {
    # 'date': 10,
    # 'month': 12,
    # 'year': 1993,
    # 'hour': 1,
    # 'minute': 25,
    # 'latitude': 25,
    # 'longitude': 82,
    'timezone': 5.5
}
horoscope_resource = "sun_sign_prediction/daily/aries"
horoscope_response = client.customCall(
    horoscope_resource,
    horoscope_data
)
print("Horoscope Response:")
print(json.dumps(horoscope_response, indent=4))

# Example 2: Premium PDF API (PDF)
pdf_data = {
    'name': "Your Name",
    'gender': "male",
    'day': 8,
    'month': 8,
    'year': 1996,
    'hour': 15,
    'minute': 46,
    'latitude': 25.5940947,
    'longitude': 85.1375645,
    'place': "Your Place",
    'tzone': 5.5
}
pdf_resource = "premium_kundli_report"

pdf_response = client.callPDF(
    pdf_resource,
    pdf_data,
   
)

print("\nPDF API Response:")
print(json.dumps(pdf_response, indent=4))
