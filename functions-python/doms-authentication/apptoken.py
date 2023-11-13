from datetime import datetime, timedelta
#import jwt
import json
from logger import logInfo, logError

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

def generateToken(username):
    logInfo('generateToken', username)
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    #jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    #return  jwt_token.decode('utf-8')
    jwt_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE0NTQ4ODEwOTh9.POQjZyC6OtqlFjmzh5S8jKkxdM90PAvI4GHzTpKwIF4'
    return jwt_token
