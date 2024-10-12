import time
from logger import logInfo, logError
import json
import jwt  # PyJWT library
import urllib.request
from jwt.algorithms import RSAAlgorithm

# Load the Auth0 domain and API audience from environment variables
AUTH0_DOMAIN = "your-auth0-domain"
AUTH0_AUDIENCE = "your-auth0-audience"

# JWKS (JSON Web Key Set) URL for Auth0
JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"

def get_jwks():
    """Fetch the JWKS from Auth0 to verify the JWT signature."""
    with urllib.request.urlopen(JWKS_URL) as response:
        return json.load(response)

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
