import jwt
import time
from logger import logInfo, logError

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 1000 * 60 * 5

def lambda_handler(event, context):
    principalId = 'Unauthorized'
    try:
        if 'authorizationToken' not in event or 'methodArn' not in event:
            return generateAuthResponse(principalId, 'Deny', methodArn)

        token = event['authorizationToken']
        methodArn = event['methodArn']

        decoded = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)

        if 'username' not in decoded or 'exp' not in decoded:
            return generateAuthResponse(principalId, 'Deny', methodArn)

        principalId = decoded['username']
        exp = decoded['exp']

        if isExpired(exp) is True:
            return generateAuthResponse(principalId, 'Deny', methodArn)
        
        return generateAuthResponse(principalId, 'Allow', methodArn)
    except Exception as error:
        logError('Exception in main function', error)
        return generateAuthResponse(principalId, 'Deny', methodArn)


def isExpired(exp):
    tokenTime = int(exp)
    currentTime = int(round(time.time() * 1000))
    return (int(currentTime) > int(tokenTime)) 

def generateAuthResponse(principalId, effect, methodArn):
    policyDocument = generatepolicyDocument(effect, methodArn)
    return {
        "principalId": principalId,
        "policyDocument": policyDocument
    }

def generatepolicyDocument(effect, methodArn):
    if (not effect or len(effect) == 0) or  (not effect or len(effect) == 0):
        return None
    
    policyDocument = {
        'Version' : '2012-10-17',
        'Statement' : [{
            "Action": "execute-api:Invoke",
            "Effect": effect,
            "Resource": methodArn
        }]
    }
    return policyDocument
