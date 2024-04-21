import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import Router

from repository import validateUserLogin
from model_login import Login
from apptoken import generateToken
from utlities import sendResponse
from DomsException import DomsException
import constants
tracer = Tracer()
logger = Logger()
router = Router()

@router.post("/token")
@tracer.capture_method
def token_generate(login: Login):
    try:
        logger.info(f"LOGIN details: {login}")

        user_login = validateUserLogin(login)
        if user_login is None:
            return sendResponse(401, {'message' : "user is not found."})
        elif json.loads(user_login)[constants.password_field_name] != login.password:
            return sendResponse(401, {'message' : "invalid user credentials"})
        elif json.loads(user_login)['login_generated'] == False:
            return sendResponse(401, {'message' : f"User '{login.username}' login is not generated."})
        else:
            token = generateToken(login)
            return sendResponse(200, {'token' : token})
    except DomsException as err:
        logger.error(f"User GetList DomsException: {err}", extra="extra info we can add here")
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"User GetList Exception: {error}")
        return sendResponse(500, {'error' : str(error)})
