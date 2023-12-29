import json
from logger import logInfo, logDebug, logError, logException

def lambda_handler(event, context):
    try:
        if 'path' not in event or 'httpMethod' not in event:
            return sendResponse(400, {'message' : 'Application service expecting http request.'})

        logInfo('Path', event['path'])
        logInfo('httpMethod', event['httpMethod'])
        logInfo('body', event['body'])

        if event['path'] == '/api/query':
            return sendResponse(200, {'message' : 'success'})
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


