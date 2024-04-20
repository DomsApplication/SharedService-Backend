import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import Router

from repository import getItemByEntityIndexPk, insertItem, deleteItem, updateItem, get_schema
from models.RepoObject import RepoObject
from utlities import sendResponse
from DomsException import DomsException
from validator import getUniqueIdFromSchema, validateRequestBodyWithDataObject, getSearchFields    

tracer = Tracer()
logger = Logger()
router = Router()

# Endpoint ------------------
@router.post("/repository")
@tracer.capture_method
def create_data_repository():
    try:
        body: dict = router.current_event.json_body  # deserialize json str to dict
        logger.info(f"REPO DICT details: {body}")
        entityName, uniquekey, uniquevalue, version, schema = validateDataRepository(body)
        
        is_valid, message = validateRequestBodyWithDataObject(schema, json.loads(body))
        logger.info("app/is_valid", is_valid)
        if not is_valid:
            raise DomsException(400, {'error' : message})

        if getItem(entityName, uniquevalue) is not None: 
            message = f"Item '{uniquevalue}' is already exists for the entity {entityName}."
            raise DomsException(406, {'message' : message})

        repoObject = RepoObject(
            unique_id = uniquevalue, 
            entity = entityName, 
            version = version, 
            payload = json.dumps(body),
            searchableField = getSearchFields(schema, json.dumps(body)))
        logger.info(f"REPO details: {repoObject}")

        insertItem(repoObject)
        message = f"Item '{uniquevalue}' is created successfully for the {entityName}."
        return sendResponse(201, {'message' : message})
    except DomsException as err:
        logger.error(f'DomsException in create_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in create_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})



###################################################
# Common functions
###################################################
@tracer.capture_method
def validateDataRepository(_body: dict):
    if _body is None:
        message = f"Request body is required."
        raise DomsException(400, message)
    elif _body["entity"] is None:
        message = f"The entity field is mandetory."
        raise DomsException(400, message)
    else:
        try:
            entityName = _body["entity"]
            schema = get_schema(entityName)
            uniquekey = getUniqueIdFromSchema(schema)

            if _body[uniquekey] is None:
                raise DomsException(400, {'error' : f"'uniqueId' field is missed in Schema {entityName}."})
            uniquevalue =  _body[uniquekey]
            if uniquevalue is None:
                raise DomsException(400, {'error' : f"'uniqueId' field value is missed in request body."})
            version = schema['version']
            return entityName, uniquekey, uniquevalue, version, schema            
        except Exception as err:
            logger.error(err)        
            raise Exception(err)

@tracer.capture_method
def getItem(entityName, uniquevalue):
    try:
        repoObject = RepoObject(
            unique_id = uniquevalue, 
            entity = entityName, 
            version = None, 
            payload = None,
            searchableField = None)
        logger.info(f"REPO details: {repoObject}")
        dataItem = getItemByEntityIndexPk(repoObject) 
        logger.info("app/dataItem", dataItem)
        return dataItem
    except Exception as err:
        logger.error(err)        
        raise Exception(err)
    

