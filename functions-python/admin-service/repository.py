import os
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger, Tracer
from utlities import getDateTimeNow
from models.RepoObject import RepoObject
import DomsException

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

def insertItem(repo: RepoObject):
    try:
        if getItemByEntityIndexPk(repo.entity, repo.unique_id) is not None: 
            message = f"Item '{repo.unique_id}' is already exists for the entity {repo.entity}."
            raise DomsException(406, message)
    except Exception as error:
        logger.error(f"validate user exist Exception: {error}")
        raise DomsException(500, {'error' : str(error)})

    try:
        item = {
            "PK" : { 'S' : repo.unique_id },
            "SK" : { 'S' : repo.unique_id },
            "ENTITIES" : { 'S' :  repo.entity },
            "MAPPINGS" : { 'S' :  repo.entity },
            "VERSION" : { 'N' :  str(repo.version) },
            "IS_DELETED" : { 'BOOL' :  False },
            "PAYLOAD" : { 'S' :  json.dumps(repo.payload) },
            "CREATED_BY" : { 'S' :  "task_user" },
            "CREATED_ON" : { 'S' :  str(getDateTimeNow()) },
            "MODIFIED_BY" : { 'S' :  "task_user" },
            "MODIFIED_ON" : { 'S' :  str(getDateTimeNow()) },
        }

        # Persist the record
        response = dynamodb_client.put_item(
            TableName = DDB_TABLE_NAME,
            Item = item
        )
        return response['ResponseMetadata']['HTTPStatusCode']
    except ClientError as err:
        exception_value = f"Exception in put item of {DDB_TABLE_NAME} for index: 'ENTITIES-IDX' for {repo.unique_id}, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logger.error(exception_value)
        raise ValueError(exception_value)


def getItemByEntityIndexPk(entity, pk):
    try:
        response = dynamodb_client.query(
            TableName = DDB_TABLE_NAME,
            IndexName = 'ENTITIES_INX',
            KeyConditionExpression = 'ENTITIES = :_ENTITIES and PK = :_pk',
            FilterExpression = 'SK = :_sk and IS_DELETED = :IS_DELETED',
            ExpressionAttributeValues = {
                ":_ENTITIES" : {
                    'S' :  str(entity)
                },
                ":_pk" : {
                    'S' :  str(pk)
                },
                ":_sk" : {
                    'S' :  str(pk)
                },
                ":IS_DELETED" : {
                    'BOOL' :  False
                }
            }
        )
        if 'Items' in response and len(response['Items']) == 0:
            return None
        elif 'Items' in response and len(response['Items']) > 1:
            exception_value = f"Duplciated item found in {DDB_TABLE_NAME} for pk: {pk} by index: 'ENTITIES-IDX'"
            logger.error(exception_value)
            raise ValueError(exception_value)
        else:
            return response['Items'][0]['PAYLOAD']['S']
    except ClientError as err:
        exception_value = f"Exception in get item {DDB_TABLE_NAME} by index: 'ENTITIES-IDX' for {pk} from the query, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logger.error(exception_value)
        raise ValueError(exception_value)
