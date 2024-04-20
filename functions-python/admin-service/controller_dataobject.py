import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import Router

from repository import getItemByEntityIndexPk, insertItem, deleteItem, updateItem
from models.RepoObject import RepoObject
from utlities import sendResponse
from DomsException import DomsException
import constants

tracer = Tracer()
logger = Logger()
router = Router()


# Endpoint ------------------
@router.post("/object")
@tracer.capture_method
def create_data_object():
    try:
        bodyObject: dict = router.current_event.json_body  # deserialize json str to dict
        logger.info(f"OBJECT DICT details: {bodyObject}")
        validateDataObject(bodyObject)

        repoObject = RepoObject(
            unique_id=bodyObject["entity"], 
            entity=constants.data_object_name, 
            version=bodyObject["version"], 
            payload=json.dumps(bodyObject),
            searchableField=None)
        logger.info(f"REPO details: {repoObject}")

        schema = getItemByEntityIndexPk(repoObject)
        if schema is not None:
            raise DomsException(400, f"{constants.data_object_name} with the name {bodyObject['entity']} is already exists.")
        logger.info(f"REPO PAYLOAD details: {repoObject.payload}")
        insertItem(repoObject)
        message = f"Item '{bodyObject['entity']}' is created successfully for the {constants.data_object_name}."
        return sendResponse(201, {'message' : message})
    except DomsException as err:
        logger.error(f'DomsException in create_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in create_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})

# Endpoint ------------------
@router.put("/object")
@tracer.capture_method
def create_data_object():
    try:
        bodyObject: dict = router.current_event.json_body  # deserialize json str to dict
        logger.info(f"OBJECT DICT details: {bodyObject}")
        validateDataObject(bodyObject)

        repoObject = RepoObject(
            unique_id=bodyObject["entity"], 
            entity=constants.data_object_name, 
            version=bodyObject["version"], 
            payload=json.dumps(bodyObject),
            searchableField=None)
        logger.info(f"REPO details: {repoObject}")

        schema = getItemByEntityIndexPk(repoObject)
        if schema is None:
            raise DomsException(400, f"{constants.data_object_name} with the name {bodyObject['entity']} is not exists.")
        logger.info(f"REPO PAYLOAD details: {repoObject.payload}")
        updateItem(repoObject)
        message = f"Item '{bodyObject['entity']}' is updated successfully for the {constants.data_object_name}."
        return sendResponse(200, {'message' : message})
    except DomsException as err:
        logger.error(f'DomsException in create_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in create_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})

# Endpoint ------------------
@router.get("/object/<object_id>")
@tracer.capture_method
def get_data_object(object_id: str):
    try:
        repoObject = RepoObject(
            unique_id=object_id, 
            entity=constants.data_object_name, 
            version=None, 
            payload=None,
            searchableField=None)

        schema = getItemByEntityIndexPk(repoObject)
        if schema is None:
            raise DomsException(400, f"'{constants.data_object_name} with the name '{object_id}' is not exists.")
        return sendResponse(200, schema)
    except DomsException as err:
        logger.error(f'DomsException in get_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in get_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})

# Endpoint ------------------
@router.delete("/object/<object_id>")
@tracer.capture_method
def delete_data_object(object_id: str):
    try:
        repoObject = RepoObject(
            unique_id=object_id, 
            entity=constants.data_object_name, 
            version=None, 
            payload=None,
            searchableField=None)

        schema = getItemByEntityIndexPk(repoObject)
        if schema is None:
            raise DomsException(400, f"'{constants.data_object_name} with the name '{object_id}' is not exists to delete.")

        deleteItem(repoObject)
        message = f"Item '{object_id}' is deleted successfully for the {constants.data_object_name}."
        return sendResponse(204, message)
    except DomsException as err:
        logger.error(f'DomsException in delete_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in delete_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})




###################################################
# Common functions
###################################################
def validateDataObject(_object: dict):
    if _object is None:
        message = f"Data-Object body is required."
        raise DomsException(400, message)
    elif _object["entity"] is None or _object["title"] is None or _object["version"] is None or _object["type"] is None:
        message = f"Required field(s) is missed. Please contact Administrator."
        raise DomsException(400, message)
    else:
        return True    
