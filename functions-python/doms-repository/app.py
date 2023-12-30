import json
from logger import logInfo, logDebug, logError, logException
from validator import validateJsonSchema, get_schema
from repository import getItemByEntityIndexPk, insertItem, updateItem, deleteItem

def lambda_handler(event, context):
    try:
        if 'path' not in event or 'httpMethod' not in event:
            return sendResponse(400, {'message' : 'Application service expecting http request.'})

        logInfo('Path', event['path'])
        logInfo('httpMethod', event['httpMethod'])
        logInfo('body', event['body'])

        if event['path'] == '/repo/write/entity':

            requestBody = json.loads(event['body'])
            if 'entity' not in requestBody:
                return sendResponse(400, {'error' : f"'entity' field is missed in request body."})
            entityName = requestBody['entity']
            
            # Getting schema from DB
            entitySchema = get_schema(entityName)

            if 'version' not in entitySchema:
                return sendResponse(400, {'error' : f"'version' field is missed in Schema {entityName}."})
            if 'uniquekey' not in entitySchema['properties']['entity']['uniquekey']:
                return sendResponse(400, {'error' : f"'entity.uniquekey' field is missed in Schema {entityName}."})

            uniquekey = entitySchema['properties']['entity']['uniquekey']
            version = entitySchema['version']

            if uniquekey not in requestBody:
                return sendResponse(400, {'error' : f"'{uniquekey}' field is missed in requesy body."})
            pk = requestBody[uniquekey]

            logInfo("app/requestBody", requestBody)
            logInfo("app/entityName", entityName)
            logInfo("app/schema.version", version)
            logInfo("app/schema.properties.entityuniquekey", uniquekey)
            logInfo("app/pk", pk)

            dbItem = getItemByEntityIndexPk(entityName, pk)
            logInfo("app/dbItem", dbItem)

            #
            # ******** Validate the input json with schame *****************
            ### INSERT
            if event['httpMethod'] == 'POST':
                if dbItem is not None: 
                    message = f"Item '{pk}' is already exists for the entity {entityName}."
                    return sendResponse(406, {'message' : message})

                try:                
                    is_valid, message = validateJsonSchema(entitySchema, requestBody)
                    logInfo("app/is_valid", is_valid)
                    if not is_valid:
                        return sendResponse(400, {'error' : message})
                except Exception as error:
                    logError('Exception in fetch schema', error)
                    return sendResponse(400, {'error' : f"Schema {entityName} not found."})

                insertItem(entityName, pk, version, requestBody)

                message = f"Item '{pk}' is created successfully for the entity {entityName}."                    
                return sendResponse(201, {'message' : message})

            ### UPDATE
            elif event['httpMethod'] == 'PUT':
                if dbItem is None: 
                    message = f"Item '{pk}' is not exists for the entity {entityName}."
                    return sendResponse(406, {'message' : message})

                try:
                    ddbPayloadObject = json.loads(dbItem)
                    ddbPayloadObject.update(requestBody) #updating the attributes(key,values) present in payload                
                    is_valid, message = validateJsonSchema(entitySchema, ddbPayloadObject)
                    logInfo("app/is_valid", is_valid)
                    if not is_valid:
                        return sendResponse(400, {'error' : message})
                except Exception as error:
                    logError('Exception in fetch schema', error)
                    return sendResponse(400, {'error' : f"Schema {entityName} not found."})

                updateItem(entityName, pk, version, ddbPayloadObject)

                message = f"Item '{pk}' is updated successfully for the entity {entityName}."                    
                return sendResponse(204, {'message' : message})

            ### DELETE
            elif event['httpMethod'] == 'DELETE':
                if dbItem is None: 
                    message = f"Item '{pk}' is not exists for the entity {entityName}."
                    return sendResponse(406, {'message' : message})

                deleteItem(entityName, pk)

                message = f"Item '{pk}' is deleted successfully for the entity {entityName}."                    
                return sendResponse(204, {'message' : message})

            else:
                msg = {'message' : 'Method: ' + event['httpMethod'] + ' not allowed for the requested path:' + event['path'] }
                return sendResponse(405, msg)    
        else:    
            msg = {'message' : 'Path :' + event['path'] + ' not found.'}
            return sendResponse(404, msg)
    except Exception as error:
        logError('Exception in main function', error)
        return sendResponse(500, {'error' : str(error)})


# Send response function
def sendResponse(code, body):
    return {
        'statusCode' : code,
        'body' : json.dumps(body),
        'headers' : {
            'Content-Type' : 'application/json'
        }
    }
