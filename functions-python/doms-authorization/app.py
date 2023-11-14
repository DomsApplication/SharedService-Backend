import jwt
import json
import time
from logger import logInfo, logError

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 1000 * 60 * 5

def lambda_handler(event, context):
    token = event['Authorization']
    logInfo('token', token)
    try:
        decoded = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
        principalId = decoded['principalId']
        exp = decoded['exp']
        logInfo('principalId', principalId)
        logInfo('exp', exp)
        policyDocument = {
            'Version' : '2012-10-17',
            'Statement' : [{
                'Action' : 'execute-api:Invoke',
                'Effect' : 'Allow',
                'Resource' : event['methodArn']
            }]
        }
    except:
        principalId = 'unauthorized',
        policyDocument = {
            'Version' : '2012-10-17',
            'Statement' : [{
                'Action' : 'execute-api:Invoke',
                'Effect' : 'Deny',
                'Resource' : event['methodArn']
            }]
        }
    return {
        'principalId' :  principalId,
        'policyDocument' : policyDocument
    }
