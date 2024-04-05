import json
from logger import logInfo, logDebug, logError, logException
from validator import validateJsonSchema, get_schema
from repository import getItemByEntityIndexPk, insertItem, updateItem, deleteItem
import DomsException

def lambda_handler(event, context):
    try:
        if 'path' not in event or 'httpMethod' not in event:
            return sendResponse(400, {'message' : 'Application service expecting http request.'})
        
        path = event['path']
        httpmethod = event['httpMethod']
        
        if httpmethod in ['POST', 'PUT']:
            if 'body' not in event:
                return sendResponse(400, {'error' : f"request body is missed for the request {path} with method {httpmethod}."})
            
            requestBody = json.loads(event['body'])
            
            if 'entity' not in requestBody:
                return sendResponse(400, {'error' : f"'entity' field is missed for the request {path} with method {httpmethod}."})

            entityName = requestBody['entity']

        elif httpmethod == 'DELETE':
            if verifyPathwithParameters(path, '/api/repo/entity/*'):
                entityName = getEntityNameFromHttpMethod(path)
            else:    
                return sendResponse(400, {'error' : f"The path '{path}' is not allowed from the method {httpmethod}."})

        elif httpmethod == 'GET':
            if not checkValidGetMethodPaths(path):
                return sendResponse(400, {'error' : f"The path '{path}' is not allowed from the method {httpmethod}."})
            entityName = getEntityNameFromHttpMethod(path)

        logInfo('path', path)
        logInfo('httpMethod', httpmethod)
        logInfo('body', requestBody)
        logInfo('entityName', entityName)

        if entityName is None:
            return sendResponse(400, {'error' : f"'entity' name is missed in the request."})

        # Getting schema from DB
        entitySchema = get_schema(entityName)
        if 'version' not in entitySchema:
            return sendResponse(400, {'error' : f"'version' field is missed in Schema {entityName}."})
        if 'uniquekey' not in entitySchema['properties']['entity']:
            return sendResponse(400, {'error' : f"'entity.uniquekey' field is missed in Schema {entityName}."})

        uniquekey = entitySchema['properties']['entity']['uniquekey']
        version = entitySchema['version']
        logInfo("app/schema.version", version)
        logInfo("app/schema.properties.entityuniquekey", uniquekey)

        ###################################
        ##### Method: POST
        ##### Path: '/api/repo/entity'
        ###################################
        if httpmethod == 'POST' and path == '/api/repo/entity':
            if uniquekey not in requestBody:
                return sendResponse(400, {'error' : f"'{uniquekey}' field is missed in requesy body."})
            pk = requestBody[uniquekey]
            dbItem = getItemByEntityIndexPk(entityName, pk)
            logInfo("app/dbItem", dbItem)

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

        ###################################
        ##### Method: POST
        ##### Path: '/api/repo/entity/bulk'
        ###################################
        elif httpmethod == 'POST' and path == '/api/repo/entity/bulk':
            ''

        ###################################
        ##### Method: PUT
        ##### Path: '/api/repo/entity'
        ###################################
        elif httpmethod == 'PUT' and path == '/api/repo/entity':
            if uniquekey not in requestBody:
                return sendResponse(400, {'error' : f"'{uniquekey}' field is missed in requesy body."})
            pk = requestBody[uniquekey]
            dbItem = getItemByEntityIndexPk(entityName, pk)
            logInfo("app/dbItem", dbItem)

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

        
        ###################################
        ##### Method: PUT
        ##### Path: '/api/repo/entity/bulk'
        ###################################
        elif httpmethod == 'PUT' and path == '/api/repo/entity/bulk':
            ''

        ###################################
        ##### Method: DELETE
        ##### Path: '/api/repo/entity/{entityname}?ids=111,123,1222,1881,199'
        ###################################
        elif httpmethod == 'DELETE' and verifyPathwithParameters(path, '/api/repo/entity/*'):
            strIds = event['queryStringParameters']['ids']
            if strIds is None:
                return sendResponse(400, {'error' : f"Path: '{path}' of DELETE method missed Ids to delete."})
            idsList = path.split(',')
            if len(idsList) > 10:
                return sendResponse(400, {'error' : f"Delete operation limit to max 10 items."})

            unsuccsList = []
            succsList = []
            for num in range(0, len(idsList)):
                pk = idsList[num]
                dbItem = getItemByEntityIndexPk(entityName, pk)
                logInfo("app/dbItem", dbItem)

                if dbItem is None: 
                    unsuccsList.append(pk)
                    continue
                else:
                    succsList.append(pk)

                deleteItem(entityName, pk)

            succsStr = ','.join(succsList) if len(succsList) > 0 else '-'
            unsuccsStr = ','.join(unsuccsList) if len(unsuccsList) > 0 else '-'
            message = f"The Items '{succsStr}'  deleted(s) successfully and Items '{unsuccsStr}' unsuccess for the entity {entityName}."                    
            return sendResponse(204, {'message' : message})

        ###################################
        ##### Method: GET
        ##### Path: '/api/repo/entity/{entityname}'
        ###################################
        elif httpmethod == 'GET' and verifyPathwithParameters(path, '/api/repo/entity/*'):
            ''
        
        ###################################
        ##### Method: GET
        ##### Path: '/api/repo/entity/{entityname}/query?search=<abc>,pageindex=1,pagesize=10,advancesearch={'firstname':'john',  'age':'greater 20'}'
        ###################################
        elif httpmethod == 'GET' and verifyPathwithParameters(path, '/api/repo/entity/*/query'):
            ''

        ###################################
        ##### Method: GET
        ##### Path: '/api/repo/entity/{entityname}/{pk}'
        ###################################
        elif httpmethod == 'GET' and verifyPathwithParameters(path, '/api/repo/entity/*/*'):
            paramsList = getPathwithParameters(path, '/api/repo/entity/*/*')
            if len(paramsList) == 0:
                return sendResponse(400, {'error' : f"Not able to read the path-patameter for the path {path} in GET method."})

            uniq_pk = paramsList[1]
            schemaItem = getItemByEntityIndexPk(entityName, uniq_pk)
            if schemaItem is None:
                return sendResponse(500, {'error' : f"Not able to read the path-patameter for the path {event['path']}"})
            return sendResponse(200, json.loads(schemaItem))

        ###################################
        ##### Method: GET
        ##### Path: '/api/repo/entity/{entityname}/{pk}/relation'
        ###################################
        elif httpmethod == 'GET' and verifyPathwithParameters(path, '/api/repo/entity/*/*/relation'):
            ''

        ###################################
        ##### Method: GET
        ##### Path: '/api/repo/entity/{entityname}/{pk}/relation/{relationname}'
        ###################################
        elif httpmethod == 'GET' and verifyPathwithParameters(path, '/api/repo/entity/*/*/relation/*'):
            ''

        else:    
            msg = {'message' : f"Method: '{httpmethod}' not allowed for the requested path:'{path}'" }
            return sendResponse(404, msg)

    except DomsException as err:
        logError('DomsException in main function', str(err))
        return sendResponse(err.error_code, {'error' : str(err.message)})
    except Exception as error:
        logError('Exception in main function', error)
        return sendResponse(500, {'error' : str(error)})

###################################
# Function: sendResponse
# Description: Send http response in application/json format
###################################
def sendResponse(code, body):
    return {
        'statusCode' : code,
        'body' : json.dumps(body),
        'headers' : {
            'Content-Type' : 'application/json'
        }
    }

###################################
# Function: getEntityNameFromHttpMethod
# Description: Get the entity name from the give path, this is applicable only for GET & DELETE methods.
###################################
def getEntityNameFromHttpMethod(path):
    try:
        paths = path.split('/')
        return paths[3] 
    except Exception as error:
        logError('Exception in getEntityNameFromGetMethod function', error)
        raise DomsException(400, f"Error while reading entity name from the path '{path}' for GET method.")
 

###################################
# Function: checkValidGetMethodPaths
# Description: Validate the 'Get' entity method paths.
###################################
def checkValidGetMethodPaths(path):
    getMethodValidPathList = ['/api/repo/entity/*', '/api/repo/entity/*/query', '/api/repo/entity/*/*', '/api/repo/entity/*/*/relation', '/api/repo/entity/*/*/relation/*']
    for pathIdx in range(0, len(getMethodValidPathList)):
        if verifyPathwithParameters(path, getMethodValidPathList[pathIdx]):
            return True
    return False

###################################
# Function: verifyPathwithParameters
# Description: verify the provided path parameter with Http Path request.
###################################
def verifyPathwithParameters(path, pathParam):
    try:
        paths = path.split('/')
        pathParams = pathParam.split('/')
        if len(paths) == len(pathParams):
            return True
        else:
            return False
    except Exception as error:
        logError('Exception in verifyPathwithParameters function', error)
        return False

###################################
# Function: getPathwithParameters
# Description: Get the path parameter dynamic values into an array.
###################################
def getPathwithParameters(path, pathParam):
    try:
        paths = path.split('/')
        pathParams = pathParam.split('/')
        list = []
        if len(paths) == len(pathParams):
            for num in range(0, len(paths)):
                if paths[num] != pathParams[num] and '*' == pathParams[num]:
                    list.append(str(paths[num]))
        return list
    except Exception as error:
        logError('Exception in getPathwithParameters function', error)
        raise Exception(error)

