import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import Router

from repository import getItemByEntityIndexPk, insertItem, deleteItem, updateItem, get_schema, getItemByEntity
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
        body = router.current_event.json_body  # deserialize json str to dict
        entityName, uniquekey, uniquevalue, version, schema = validateDataRepository(body)
        is_valid, message = validateRequestBodyWithDataObject(schema, body)
        if not is_valid:
            raise DomsException(400, {'error' : str(message)})
        if getItem(entityName, uniquevalue) is not None: 
            message = f"Item '{uniquevalue}' is already exists for the entity {entityName}."
            raise DomsException(406, {'message' : message})
        repoObject = RepoObject(
            unique_id = uniquevalue, 
            entity = entityName, 
            version = version, 
            payload = json.dumps(body),
            searchableField = getSearchFields(schema, body))
        logger.info(f'REPO OBJECT::: {repoObject}')
        insertItem(repoObject)
        message = f"Item '{uniquevalue}' is created successfully for the {entityName}."
        return sendResponse(201, {'message' : message})
    except DomsException as err:
        logger.error(f'DomsException in create_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in create_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})

# Endpoint ------------------
@router.put("/repository")
@tracer.capture_method
def update_data_repository():
    try:
        body = router.current_event.json_body
        entityName, uniquekey, uniquevalue, version, schema = validateDataRepository(body)

        dbItem = getItem(entityName, uniquevalue) 
        if dbItem is None: 
            message = f"Item '{uniquevalue}' is not exists for the entity {entityName}."
            raise DomsException(406, {'message' : message})

        _body = json.loads(dbItem)
        _body.update(body) #updating the attributes(key,values) present in payload 

        is_valid, message = validateRequestBodyWithDataObject(schema, _body)
        if not is_valid:
            raise DomsException(400, {'error' : str(message)})

        repoObject = RepoObject(
            unique_id = uniquevalue, 
            entity = entityName, 
            version = version, 
            payload = json.dumps(_body),
            searchableField = getSearchFields(schema, _body))
        logger.info(f'REPO OBJECT::: {repoObject}')
        updateItem(repoObject)
        message = f"Item '{uniquevalue}' is updated successfully for the {entityName}."
        return sendResponse(200, {'message' : message})
    except DomsException as err:
        logger.error(f'DomsException in create_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in create_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})

# Endpoint ------------------
@router.delete("/repository/<entity_id>/<repository_id>")
@tracer.capture_method
def delete_data_repository(entity_id: str, repository_id: str):
    try:
        repoObject = RepoObject(
            unique_id = repository_id, 
            entity = entity_id, 
            version = None, 
            payload = None,
            searchableField = None)

        data = getItemByEntityIndexPk(repoObject)
        if data is None:
            raise DomsException(400, f"'{entity_id} with the name '{repository_id}' is not exists to delete.")
        deleteItem(repoObject)
        message = f"Item '{repository_id}' is deleted successfully for the object {entity_id}."
        return sendResponse(204, message)
    except DomsException as err:
        logger.error(f'DomsException in delete_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in delete_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})

# Endpoint ------------------
@router.get("/repository/<entity_id>")
@tracer.capture_method
def get_data_object(entity_id: str):
    try:
        schema = get_schema(entity_id)
        if schema is None:
            raise DomsException(400, f"'Entity with the name '{entity_id}' is not exists.")

        data = getItemByEntity(entity_id)
        if data is None:
            raise DomsException(400, f"Record not found for the entity with the name '{entity_id}'.")
        return sendResponse(200, data)
    except DomsException as err:
        logger.error(f'DomsException in get_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in get_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})

# Endpoint ------------------
@router.get("/repository/<entity_id>/<repository_id>")
@tracer.capture_method
def get_specific_data_object(entity_id: str, repository_id: str):
    try:
        repoObject = RepoObject(
            unique_id = repository_id, 
            entity = entity_id, 
            version = None, 
            payload = None,
            searchableField = None)

        data = getItemByEntityIndexPk(repoObject)
        if data is None:
            raise DomsException(400, f"'{entity_id} with the name '{repository_id}' is not exists.")
        return sendResponse(200, data)
    except DomsException as err:
        logger.error(f'DomsException in get_data_object: {str(err.message)}')
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logger.error(f"Exception in get_data_object: {error}")
        return sendResponse(500, {'error' : str(error)})

###################################################
# Common functions
###################################################
@tracer.capture_method
def validateDataRepository(_body):
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
        dataItem = getItemByEntityIndexPk(repoObject) 
        return dataItem
    except Exception as err:
        logger.error(err)        
        raise Exception(err)
    

