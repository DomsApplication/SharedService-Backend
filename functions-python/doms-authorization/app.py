import boto3
import sys
import os
import json
import uuid
from datetime import datetime

def lambda_handler(event, context):
    print('Request from AUTHORIZATION...')
    print('OS ::: ' , os.name)
    print('Python version ::: ' , sys.version)
    print('Version info ::: ' , sys.version_info)

    print('event :::', event)

    response = {
        'id': str(uuid.uuid4()),
        'date': str(datetime.timestamp(datetime.now())),
        'stage': 'DEV',
        'message': 'Hello World!...'
    }

    print(response)

    return {
        'statusCode': 200,
        'headers': {},
        'body': json.dumps(response)
    }