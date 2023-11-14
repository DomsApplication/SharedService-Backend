import time
import jwt
from logger import logInfo, logError

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 1000 * 60 * 5

def generateToken(username):
    logInfo('generateToken', username)
    payload = {
        'username': username,
        'exp': str(round(time.time() * 1000) + JWT_EXP_DELTA_SECONDS)
    }
    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    logInfo('jwt_token/encode', jwt_token)
    logInfo('jwt_token/decode', str(jwt.decode(jwt_token, JWT_SECRET, JWT_ALGORITHM)))
    return jwt_token
