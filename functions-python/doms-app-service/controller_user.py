from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler import Response

from repository import getItemByEntityIndexPk, insertItem, updateItem, deleteItem
from model_user import User
from app import sendResponse
import DomsException

tracer = Tracer()
logger = Logger()
router = Router()

@router.post("/user")
@tracer.capture_method
def insert_user(user: User) -> Response:
    try:
        insertItem(user.entity, user.unique_id, user.version, user)
        message = f"Item '{user.unique_id}' is created successfully for the entity {user.entity}."                    
        return sendResponse(201, {'message' : message})
    except DomsException as err:
        logger.error(f"User Insert DomsException: {err}", extra="extra info we can add here")
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"User Insert Exception: {error}")
        return sendResponse(500, {'error' : str(error)})

@router.get("/user")
@tracer.capture_method
def get_list_of_users() -> Response:
    try:
        user_list = [ {"entity":"user", "unique_id":"rama@test.com", "first_name":"rama"}, 
            {"entity":"user", "unique_id":"bama@test.com", "first_name":"bama"} ]
        return sendResponse(200, user_list)
    except DomsException as err:
        logger.error(f"User GetList DomsException: {err}", extra="extra info we can add here")
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"User GetList Exception: {error}")
        return sendResponse(500, {'error' : str(error)})




