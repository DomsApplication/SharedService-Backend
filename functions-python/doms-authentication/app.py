import boto3
import sys
import os
import json
import uuid
from datetime import datetime
from logger import logInfo, logError
from jwt import generateToken

def lambda_handler(event, context):
    try:
        
        if('path' not in event or 'httpMethod' not in event):
            return sendResponse(400, json.dumps({'message' : 'Authentication service expecting http request.'}))

        logInfo('Path', event['path'])
        logInfo('httpMethod', event['httpMethod'])
        logInfo('body', event['body'])

        if(event['path'] == '/auth/token' and event['httpMethod'] == 'POST'):
            return generateToken(event, context)
        else:
            invalidRequest(event)

    except Exception as error:
        logError('Exception in main function', error)
        return sendErrorResponse(500, str(error), context)




### Send http response
def sendResponse(statusCode, body): 
    return {
        'statusCode': statusCode,
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

### Send http response
def sendErrorResponse(statusCode, body, context): 
    response = {
        'status': statusCode,
        'errors': body
    }
    return context.fail(json.stringify(response));


### Generate JWT token
def generateToken(event, context):
    if('body' not in event):
        return sendErrorResponse(400, json.dumps({'message' : "Request body was missed. Kindly provide 'username' & 'password' in json format."}), context)

    user = json.loads(event['body'])

    if('username' not in user or 'password' not in user):    
        return sendResponse(400, json.dumps({'message' : "Invalid Request. Kindly provide 'username' & 'password' in json format."}))
    
    if(user['username'] != 'system' and user['password'] != 'Password1#'):
        return sendResponse(401, json.dumps({'message' : "invalid user credentials"}))

    token = generateToken(user['username'])
    return sendResponse(200, json.dumps({'token' : token}))




### Respond Invalid request
def invalidRequest(event):
    msg = {'message' : 'Requested path :' + event['path'] + ' and httpMethod:' + event['httpMethod'] + ' not allowed.'}
    return sendResponse(405, json.dumps(msg))    

