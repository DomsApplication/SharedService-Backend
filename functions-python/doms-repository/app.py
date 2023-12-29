import json
from logger import logInfo, logDebug, logError, logException
from validator import validateJsonSchema, get_schema

def lambda_handler(event, context):
    try:
        if 'path' not in event or 'httpMethod' not in event:
            return sendResponse(400, {'message' : 'Application service expecting http request.'})

        logInfo('Path', event['path'])
        logInfo('httpMethod', event['httpMethod'])
        logInfo('body', event['body'])

        if event['path'] == '/api/payload/entity':
            
            requestBody = json.loads(event['body'])
            entityName = requestBody['entity']

            entitySchema = get_schema(entityName)
            is_valid, message = validateJsonSchema(entitySchema, requestBody)
            if not is_valid:
                return sendResponse(400, {'error' : message})

            #
            # ******** Validate the input json with schame *****************
            ### INSERT
            if event['httpMethod'] == 'POST':
                return sendResponse(200, {'message' : 'success'})

            ### UPDATE
            elif event['httpMethod'] == 'PUT':
                return sendResponse(200, {'message' : 'success'})

            ### DELETE
            elif event['httpMethod'] == 'DELETE':
                return sendResponse(200, {'message' : 'success'})

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


