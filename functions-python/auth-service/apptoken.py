import time
import jwt
from model_login import Login
from aws_lambda_powertools import Logger, Tracer

tracer = Tracer()
logger = Logger()

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 1000 * 60 * 5

@tracer.capture_method
def generateToken(login: Login):
    logger.info(f'generateToken {login.username}')
    payload = {
        'username': login.username,
        'exp': str(round(time.time() * 1000) + JWT_EXP_DELTA_SECONDS)
    }
    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    logger.info(f'jwt_token/encode {jwt_token}')
    logger.info(f'jwt_token/decode {str(jwt.decode(jwt_token, JWT_SECRET, JWT_ALGORITHM))}')
    return jwt_token
