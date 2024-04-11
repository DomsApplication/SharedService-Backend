from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import Router

from model_login import Login
from apptoken import generateToken
from utlities import sendResponse
import DomsException

tracer = Tracer()
logger = Logger()
router = Router()

_username = "system"
_password = "Password1#"

@router.post("/token")
@tracer.capture_method
def create_user(login: Login):
    try:
        logger.info(f"LOGIN details: {login}")
        return genToken(login)
    except DomsException as err:
        logger.error(f"User GetList DomsException: {err}", extra="extra info we can add here")
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"User GetList Exception: {error}")
        return sendResponse(500, {'error' : str(error)})

### Generate JWT token
@tracer.capture_method
def genToken(login: Login):
    if _username != login.username or _password != login.password:
        return sendResponse(401, {'message' : "invalid user credentials"})

    token = generateToken(login)    
    return sendResponse(200, {'token' : token})
