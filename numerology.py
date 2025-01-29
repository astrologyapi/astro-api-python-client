
from dotenv import load_dotenv
import os
from sdk import AstrologyAPIClient

# Load environment variables from .env file
load_dotenv()

userID = os.getenv('ASTROLOGY_API_USER_ID')
apiKey = os.getenv('ASTROLOGY_API_KEY') 

dateOfBirth = 25
monthOfBirth = 12
yearOfBirth = 1988
name = 'Your Name'

# Numerology APIs which needs to be called
resource = 'numero_table'

# instantiate AstrologyAPIClient class
astrologyAPI= AstrologyAPIClient(userID, apiKey)

# call numerology method of the AstrologyAPIClient
numeroData = astrologyAPI.numeroCall(resource, dateOfBirth, monthOfBirth, yearOfBirth, name)

# printing data
print(numeroData)