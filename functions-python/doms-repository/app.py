import os
import json
from logger import logInfo, logDebug, logError, logException
from validator import validateJson
def lambda_handler(event, context):
    try:
        logInfo('## ENVIRONMENT VARIABLES', os.environ)
        logInfo('LAMBDA_ARN', context.invoked_function_arn)
        logInfo('LAMBDA_ACCOUNT', context.invoked_function_arn.split(":")[4])
        logDebug('EVENT', event)

        data = {
            "unique_id" : "Sri",
            "name" : "Rama"
        }
        validateJson("user", data)

        return {
            'statusCode': 200,
            'body': json.dumps('Welcome to repository Lambda!')
        }
    except Exception as error:
        logException(error)
        raise Exception(error)
