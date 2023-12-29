import json
from logger import logInfo, logDebug, logError, logException
from validator import validateJson

def lambda_handler(event, context):
    try:
        if 'path' not in event or 'httpMethod' not in event:
            return sendResponse(400, {'message' : 'Application service expecting http request.'})

        logInfo('Path', event['path'])
        logInfo('httpMethod', event['httpMethod'])
        logInfo('body', event['body'])

        #
        # ******** Validate the input json with schame *****************
        if event['httpMethod'] == 'POST' or event['httpMethod'] == 'PUT':

            if 'body' not in event:
                return sendResponse(400, {'message' : "Request body was missed. Kindly provide in json format."})
            
            requestBody = json.loads(event['body'])

            #
            #TODO: need to handle separate the parent & child entity and do validation. 
            #
            logInfo("validateJson/BEFORE", requestBody)    
            is_valid, message = validateJson("user", requestBody)
            if not is_valid:
                return sendResponse(400, {'error' : message})

        #
        # ******** Validate the input json with schame *****************
        ### INSERT
        if event['path'] == '/repo/write/entity' and event['httpMethod'] == 'POST':
            return sendResponse(200, {'message' : 'success'})

        ### UPDATE
        elif event['path'] == '/repo/write/entity' and event['httpMethod'] == 'PUT':
            return sendResponse(200, {'message' : 'success'})

        ### DELETE
        elif event['path'] == '/repo/write/entity' and event['httpMethod'] == 'DELETE':
            return sendResponse(200, {'message' : 'success'})

        else:
            msg = {'message' : 'Requested path :' + event['path'] + ' and httpMethod:' + event['httpMethod'] + ' not allowed.'}
            return sendResponse(405, msg)    
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