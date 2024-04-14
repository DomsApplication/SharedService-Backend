import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import Router

from repository import getItemByEntityIndexPk, insertItem, deleteItem
from models.RepoObject import RepoObject
from utlities import sendResponse, validateDataObject
from DomsException import DomsException

tracer = Tracer()
logger = Logger()
router = Router()

data_object_name = 'DATA_OBJECT'

@router.post("/object")
@tracer.capture_method
def create_data_object():
    try:
        bodyObject: dict = router.current_event.json_body  # deserialize json str to dict
        logger.info(f"OBJECT DICT details: {bodyObject}")
        validateDataObject(bodyObject)

        repoObject = RepoObject(
            unique_id=bodyObject["entity"], 
            entity=data_object_name, 
            version=bodyObject["version"], 
            payload=json.dumps(bodyObject),
            searchableField=None)
        logger.info(f"REPO details: {repoObject}")

        schema = getItemByEntityIndexPk(repoObject)
        if schema is not None:
            raise DomsException(400, f"{data_object_name} with the name {bodyObject['entity']} is already exists.")
        logger.info(f"REPO PAYLOAD details: {repoObject.payload}")
        insertItem(repoObject)
        message = f"Item '{bodyObject['entity']}' is created successfully for the {data_object_name}."                    
        return sendResponse(201, {'message' : message})
    except DomsException as err:
        logger.error(f'DomsException in create_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in create_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})

@router.get("/object/<object_id>")
@tracer.capture_method
def get_data_object(object_id: str):
    try:
        repoObject = RepoObject(
            unique_id=object_id, 
            entity=data_object_name, 
            version=None, 
            payload=None,
            searchableField=None)

        schema = getItemByEntityIndexPk(repoObject)
        if schema is None:
            raise DomsException(400, f"'{data_object_name} with the name '{object_id}' is not exists.")
        return sendResponse(200, schema)
    except DomsException as err:
        logger.error(f'DomsException in get_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in get_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})

@router.delete("/object/<object_id>")
@tracer.capture_method
def delete_data_object(object_id: str):
    try:
        repoObject = RepoObject(
            unique_id=object_id, 
            entity=data_object_name, 
            version=None, 
            payload=None,
            searchableField=None)

        schema = getItemByEntityIndexPk(repoObject)
        if schema is None:
            raise DomsException(400, f"'{data_object_name} with the name '{object_id}' is not exists to delete.")

        deleteItem(repoObject)
        return sendResponse(200, schema)
    except DomsException as err:
        logger.error(f'DomsException in delete_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in delete_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})
