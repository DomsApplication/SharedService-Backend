import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from logger import logInfo, logDebug, logError, logException

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
            ExpressionAttributeValues = {
                ":_ENTITIES" : {
                    'S' :  str(entity)
                },
                ":_pk" : {
                    'S' :  str(pk)
                }
            },
            KeyConditionExpression = 'ENTITIES = :_ENTITIES and PK = :_pk'
        )
        if 'Items' in response and len(response['Items']) > 0:
            return response['Items'][0]['PAYLOAD']['S']
        return ''
    except ClientError as err:
        exception_value = f"Can not query shavika-doms-backend-doms by index: 'ENTITIES-IDX', {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logException(exception_value)
        raise ValueError(exception_value)
