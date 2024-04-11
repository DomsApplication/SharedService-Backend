import os
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger, Tracer
from utlities import getDateTimeNow
from validator import getSearchFieldsByEntityName, getSearchFields

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

def insertItem(entity, pk, version, payload):
    try:
        item = {
            "PK" : { 'S' : pk },
            "SK" : { 'S' : pk },
            "ENTITIES" : { 'S' :  entity },
            "MAPPINGS" : { 'S' :  entity },
            "VERSION" : { 'N' :  str(version) },
            "IS_DELETED" : { 'BOOL' :  False },
            "PAYLOAD" : { 'S' :  json.dumps(payload) },
            "CREATED_BY" : { 'S' :  "task_user" },
            "CREATED_ON" : { 'S' :  str(getDateTimeNow()) },
            "MODIFIED_BY" : { 'S' :  "task_user" },
            "MODIFIED_ON" : { 'S' :  str(getDateTimeNow()) },
        }

        # Add the searchable fields into Dynamo table item.
        searchableField = getSearchFieldsByEntityName(entity, payload)    
        for serField in searchableField:
            for serFieldKey in serField:
                val = {}
                val[dynamoDBDataType(serField['type'])] = serField[serFieldKey]
                item[f'{serFieldKey}'] = val

        # Persist the record
        response = dynamodb_client.put_item(
            TableName = DDB_TABLE_NAME,
            Item = item
        )
        return response['ResponseMetadata']['HTTPStatusCode']
    except ClientError as err:
        exception_value = f"Exception in put item of {DDB_TABLE_NAME} for index: 'ENTITIES-IDX' for {pk}, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logger.error(exception_value)
        raise ValueError(exception_value)

def updateItem(entity, pk, version, payload):
    try:
        # Init update-expression
        update_expression = 'SET  #payload = :payload, #version = :version, #modifiedby = :modifiedby, #modifiedon = :modifiedon'
        # Build expression-attribute-names, expression-attribute-values, and the update-expression
        expression_attribute_names = {
                '#payload': 'PAYLOAD',
                '#version': 'VERSION', 
                '#modifiedby':'MODIFIED_BY', 
                '#modifiedon':'MODIFIED_ON'
        }
        expression_attribute_values = {
                ':payload': {'S' : json.dumps(payload)},
                ':version': {'S' : str(version)},
                ':modifiedby': {'S' : 'task_user'},
                ':modifiedon': {'S' : str(getDateTimeNow())},
                ':_ENTITIES' : {'S' : str(entity)}
        }

        # Add the searchable fields into Dynamo table item.
        searchableField = getSearchFieldsByEntityName(entity, payload)    
        for serField in searchableField:
            for serFieldKey in serField:
                update_expression += f' #{serFieldKey} = :{serFieldKey},'  # Notice the "#" to solve issue with reserved keywords
                expression_attribute_names[f'#{serFieldKey}'] = serFieldKey
                val = {}
                val[dynamoDBDataType(serField['type'])] = serField[serFieldKey]
                expression_attribute_values[f':{serFieldKey}'] = val

        response = dynamodb_client.update_item(
            TableName=DDB_TABLE_NAME,
            Key={
                'PK': {'S': pk},
                'SK': {'S': pk}
            },
            ConditionExpression = 'ENTITIES = :_ENTITIES',
            UpdateExpression = update_expression,
            ExpressionAttributeNames = expression_attribute_names,  
            ExpressionAttributeValues =  expression_attribute_values,  
            ReturnValues='ALL_NEW'  
        )
        return response['ResponseMetadata']['HTTPStatusCode']
    except ClientError as err:
        exception_value = f"Exception in put item of {DDB_TABLE_NAME} for index: 'ENTITIES-IDX' for {pk}, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logger.error(exception_value)
        raise ValueError(exception_value)


def deleteItem(entity, pk):
    try:
        response = dynamodb_client.delete_item(
            TableName=DDB_TABLE_NAME,
            Key={
                'PK': { 'S': str(pk), },
                'SK': { 'S': str(pk), }
            },
            ConditionExpression='ENTITIES = :_ENTITIES',
            ExpressionAttributeValues = {
                ":_ENTITIES" : {
                    'S' :  str(entity)
                }
            }
        )
        return response['ResponseMetadata']['HTTPStatusCode']
    except ClientError as err:
        exception_value = f"Exception in put item of {DDB_TABLE_NAME} for index: 'ENTITIES-IDX' for {pk}, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
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

def dynamoDBDataType(dataType):
    dType = 'S'
    match dataType:
        case 'string':
            dType = 'S'
        case 'boolean':
            dType = 'BOOL'
        case 'integer':
            dType = 'N'
    return dType

