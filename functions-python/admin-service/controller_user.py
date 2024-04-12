import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import Router
from pydantic import ValidationError

from repository import getItemByEntityIndexPk
from models.user import User
from models.RepoObject import RepoObject
from utlities import sendResponse
import DomsException

tracer = Tracer()
logger = Logger()
router = Router()

@router.post("/user")
@tracer.capture_method
def create_user(user: User):
    try:
        logger.info(f"USER details: {user}")
        repoObject = RepoObject(unique_id=user.unique_id, entity=user.entity, version=user.version, payload=user.json(), searchableField=user.json())
        logger.info(f"REPO details: {repoObject}")

        if getItemByEntityIndexPk(user.entity, user.unique_id) is not None: 
            message = f"Item '{user.unique_id}' is already exists for the entity {user.entity}."
            raise Exception(message)

        message = f"Item '{user.unique_id}' is created successfully for the entity {user.entity}."                    
        return sendResponse(201, {'message' : message})
    except Exception as error:
        logger.error(f"User GetList Exception: {error}")
        return sendResponse(500, {'error' : str(error)})

@router.get("/user")
@tracer.capture_method
def get_list_of_users():
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
