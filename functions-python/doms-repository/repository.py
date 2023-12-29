import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from logger import logInfo, logDebug, logError, logException
from utlities import getDateTimeNow

# https://www.fernandomc.com/posts/ten-examples-of-getting-data-from-dynamodb-with-python-and-boto3/
# https://stackoverflow.com/questions/35758924/how-do-we-query-on-a-secondary-index-of-dynamodb-using-boto3

AWS_REGION_NAME = os.environ['AWS_Region']
DDB_TABLE_NAME = os.environ['DDB_TABLE_NAME']

# Creating the DynamoDB Client
dynamodb_client = boto3.client('dynamodb', region_name = AWS_REGION_NAME)

# Creating the DynamoDB Table Resource
dynamodb = boto3.resource('dynamodb', region_name = AWS_REGION_NAME)
table = dynamodb.Table(DDB_TABLE_NAME)

def getItemByEntityIndexPk(entity, pk):
    try:
        response = dynamodb_client.query(
            TableName = DDB_TABLE_NAME,
            IndexName = 'ENTITIES_INX',
            KeyConditionExpression = 'ENTITIES = :_ENTITIES and PK = :_pk',
            FilterExpression = 'SK = :_sk',
            ExpressionAttributeValues = {
                ":_ENTITIES" : {
                    'S' :  str(entity)
                },
                ":_pk" : {
                    'S' :  str(pk)
                },
                ":_sk" : {
                    'S' :  str(pk)
                }
            }
        )
        if 'Items' in response and len(response['Items']) == 0:
            return None
        elif 'Items' in response and len(response['Items']) > 1:
            exception_value = f"Duplciated item found in {DDB_TABLE_NAME} for pk: {pk} by index: 'ENTITIES-IDX'"
            logException(exception_value)
            raise ValueError(exception_value)
        else:
            return response['Items'][0]['PAYLOAD']['S']
    except ClientError as err:
        exception_value = f"Exception in get item {DDB_TABLE_NAME} by index: 'ENTITIES-IDX' for {pk} from the query, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logException(exception_value)
        raise ValueError(exception_value)

def insertItem(entity, pk, version, payload):
    try:
        item = {
            "PK" : { 'S' :  str(pk) },
            "SK" : { 'S' :  str(pk) },
            "ENTITIES" : { 'S' :  str(entity) },
            "MAPPINGS" : { 'S' :  str(entity) },
            "VERSION" : { 'N' :  version },
            "PAYLOAD" : { 'S' :  payload },
            "CREATED_BY" : { 'S' :  "task_user" },
            "CREATED_ON" : { 'S' :  str(getDateTimeNow()) },
            "MODIFIED_BY" : { 'S' :  "task_user" },
            "MODIFIED_ON" : { 'S' :  str(getDateTimeNow()) },
        }
        response = dynamodb.put_item(
            TableName = DDB_TABLE_NAME,
            Item = item
        )
        return response['ResponseMetadata']['HTTPStatusCode']
    except ClientError as err:
        exception_value = f"Exception in put item of {DDB_TABLE_NAME} for index: 'ENTITIES-IDX' for {pk}, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logException(exception_value)
        raise ValueError(exception_value)
