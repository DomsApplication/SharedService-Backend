import boto3
import sys
import os
import json
import uuid
from datetime import datetime
from logger import logInfo, logError

def lambda_handler(event, context):
    try:
        
        if('path' not in event or 'httpMethod' not in event):
            return sendResponse(400, json.dumps({'message' : 'Authentication service expecting http request.'}))

        logInfo('Path', event['path'])
        logInfo('httpMethod', event['httpMethod'])
        logInfo('body', event['body'])

        if('/token' in event['path'] and event['httpMethod'] == 'POST'):
            msg = {'token' : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE0NTQ4ODEwOTh9.POQjZyC6OtqlFjmzh5S8jKkxdM90PAvI4GHzTpKwIF4'}
            return sendResponse(200, json.dumps(msg))
        else:
            msg = {'message' : 'Requested path :' + event['path'] + ' and httpMethod:' + event['httpMethod'] + ' not allowed.'}
            return sendResponse(405, json.dumps(msg))    

    except Exception as error:
        logError('Exception in main function', error)
        return sendResponse(500, str(error))

def sendResponse(statusCode, body):
    return {
        'statusCode': statusCode,
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }