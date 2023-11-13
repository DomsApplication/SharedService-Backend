from datetime import datetime, timedelta
import jwt
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
    logInfo('payload', payload)
    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    logInfo('jwt_token', jwt_token)
    return  jwt_token.decode('utf-8')
