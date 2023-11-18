import json
from logger import logInfo, logError
from apptoken import generateToken

def lambda_handler(event, context):
    try:
        logInfo('event', event)
        if 'path' not in event or 'httpMethod' not in event:
            return sendResponse(400, {'message' : 'Authentication service expecting http request.'})

        logInfo('Path', event['path'])
        logInfo('httpMethod', event['httpMethod'])
        logInfo('body', event['body'])
        logInfo('Path_Exists', event['path'] == '/auth/token')
        logInfo('Http_Exists', event['httpMethod'] == 'POST')

        if event['path'] == '/auth/token' and event['httpMethod'] == 'POST':
            return genToken(event)
        else:
            msg = {'message' : 'Requested path :' + event['path'] + ' and httpMethod:' + event['httpMethod'] + ' not allowed.'}
            return sendResponse(405, msg)    
        
    except Exception as error:
        logError('Exception in main function', error)
        return sendResponse(500, {'error' : str(error)})

### Generate JWT token
def genToken(event):
    logInfo('GetToken/body', event['body'])
    if 'body' not in event:
        return sendResponse(400, {'message' : "Request body was missed. Kindly provide 'username' & 'password' in json format."})
    
    requestBody = json.loads(event['body'])
    logInfo('GetToken/requestBody', requestBody)

    if 'system' != requestBody['username'] or 'Password1#' != requestBody['password']:
        return sendResponse(401, {'message' : "invalid user credentials"})

    token = generateToken(requestBody['username'])    
    return sendResponse(200, {'token' : token})

# Send response function
def sendResponse(code, body):
    return {
        'statusCode' : code,
        'body' : json.dumps(body),
        'headers' : {
            'Content-Type' : 'application/json'
        }
    }