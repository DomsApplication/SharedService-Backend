import os
import json
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger, Tracer
from utlities import getDateTimeNow
from model_login import Login
import constants

tracer = Tracer()
logger = Logger()

# https://www.fernandomc.com/posts/ten-examples-of-getting-data-from-dynamodb-with-python-and-boto3/
# https://stackoverflow.com/questions/35758924/how-do-we-query-on-a-secondary-index-of-dynamodb-using-boto3

AWS_REGION_NAME = os.environ['AWS_Region']
DDB_TABLE_NAME = os.environ['DDB_TABLE_NAME']

# Creating the DynamoDB Client
dynamodb_client = boto3.client('dynamodb', region_name = AWS_REGION_NAME)

# Creating the DynamoDB Table Resource
dynamodb = boto3.resource('dynamodb', region_name = AWS_REGION_NAME)
table = dynamodb.Table(DDB_TABLE_NAME)

@tracer.capture_method
def validateUserLogin(login: Login):
    try:
        response = dynamodb_client.query(
            TableName = DDB_TABLE_NAME,
            IndexName = 'ENTITIES_INX',
            KeyConditionExpression = 'ENTITIES = :_ENTITIES',
            FilterExpression = f'{constants.user_id_field_name} = :{constants.user_id_field_name} or {constants.email_id_field_name} = :{constants.email_id_field_name}',
            ExpressionAttributeValues = {
                ":_ENTITIES" : {
                    'S' :  str(constants.user_object_name)
                },
                f":{constants.user_id_field_name}" : {
                    'S' :  str(login.username)
                },
                f":{constants.email_id_field_name}" : {
                    'S' :  str(login.username)
                }
            }
        )
        if 'Items' in response and len(response['Items']) == 0:
            return None
        elif 'Items' in response and len(response['Items']) > 1:
            exception_value = f"Duplciated item found in {DDB_TABLE_NAME} for  {login.username} by index: 'ENTITIES-IDX'"
            logger.error(exception_value)
            raise ValueError(exception_value)
        else:
            return response['Items'][0]['PAYLOAD']['S']
    except ClientError as err:
        exception_value = f"Exception in get item {DDB_TABLE_NAME} by index: 'ENTITIES-IDX' for {login.username} from the query, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logger.error(exception_value)
        raise ValueError(exception_value)
