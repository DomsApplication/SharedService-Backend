import os
import json
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger, Tracer
from utlities import getDateTimeNow
from models.RepoObject import RepoObject

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
def insertItem(repo: RepoObject):
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

        # Add the searchable fields into Dynamo table item.
        if repo.searchableField is not None:   
            for serField in repo.searchableField:
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
        exception_value = f"Exception in put item of {DDB_TABLE_NAME} for index: 'ENTITIES-IDX' for {repo.unique_id}, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logger.error(exception_value)
        raise ValueError(exception_value)

@tracer.capture_method
def updateItem(repo: RepoObject):
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
                ':payload': {'S' : json.dumps(repo.payload)},
                ':version': {'S' : str(repo.version)},
                ':modifiedby': {'S' : 'task_user'},
                ':modifiedon': {'S' : str(getDateTimeNow())},
                ':_ENTITIES' : {'S' : str(repo.entity)}
        }

        # Add the searchable fields into Dynamo table item.
        if repo.searchableField is not None:  
            for serField in repo.searchableField:
                for serFieldKey in serField:
                    update_expression += f' #{serFieldKey} = :{serFieldKey},'  # Notice the "#" to solve issue with reserved keywords
                    expression_attribute_names[f'#{serFieldKey}'] = serFieldKey
                    val = {}
                    val[dynamoDBDataType(serField['type'])] = serField[serFieldKey]
                    expression_attribute_values[f':{serFieldKey}'] = val

        response = dynamodb_client.update_item(
            TableName=DDB_TABLE_NAME,
            Key={
                'PK': {'S': repo.unique_id},
                'SK': {'S': repo.unique_id}
            },
            ConditionExpression = 'ENTITIES = :_ENTITIES',
            UpdateExpression = update_expression,
            ExpressionAttributeNames = expression_attribute_names,  
            ExpressionAttributeValues =  expression_attribute_values,  
            ReturnValues='ALL_NEW'  
        )
        return response['ResponseMetadata']['HTTPStatusCode']
    except ClientError as err:
        exception_value = f"Exception in put item of {DDB_TABLE_NAME} for index: 'ENTITIES-IDX' for {repo.unique_id}, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logger.error(exception_value)
        raise ValueError(exception_value)

@tracer.capture_method
def deleteItem(repo: RepoObject):
    try:
        response = dynamodb_client.delete_item(
            TableName=DDB_TABLE_NAME,
            Key={
                'PK': { 'S': str(repo.unique_id), },
                'SK': { 'S': str(repo.unique_id), }
            },
            ConditionExpression='ENTITIES = :_ENTITIES',
            ExpressionAttributeValues = {
                ":_ENTITIES" : {
                    'S' :  str(repo.entity)
                }
            }
        )
        return response['ResponseMetadata']['HTTPStatusCode']
    except ClientError as err:
        exception_value = f"Exception in put item of {DDB_TABLE_NAME} for index: 'ENTITIES-IDX' for {repo.unique_id}, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logger.error(exception_value)
        raise ValueError(exception_value)

@tracer.capture_method
def getItemByEntityIndexPk(repo: RepoObject):
    try:
        response = dynamodb_client.query(
            TableName = DDB_TABLE_NAME,
            IndexName = 'ENTITIES_INX',
            KeyConditionExpression = 'ENTITIES = :_ENTITIES and PK = :_pk',
            FilterExpression = 'SK = :_sk and IS_DELETED = :IS_DELETED',
            ExpressionAttributeValues = {
                ":_ENTITIES" : {
                    'S' :  str(repo.entity)
                },
                ":_pk" : {
                    'S' :  str(repo.unique_id)
                },
                ":_sk" : {
                    'S' :  str(repo.unique_id)
                },
                ":IS_DELETED" : {
                    'BOOL' :  False
                }
            }
        )
        if 'Items' in response and len(response['Items']) == 0:
            return None
        elif 'Items' in response and len(response['Items']) > 1:
            exception_value = f"Duplciated item found in {DDB_TABLE_NAME} for pk: {repo.unique_id} by index: 'ENTITIES-IDX'"
            logger.error(exception_value)
            raise ValueError(exception_value)
        else:
            return response['Items'][0]['PAYLOAD']['S']
    except ClientError as err:
        exception_value = f"Exception in get item {DDB_TABLE_NAME} by index: 'ENTITIES-IDX' for {repo.unique_id} from the query, {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        logger.error(exception_value)
        raise ValueError(exception_value)

@tracer.capture_method
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