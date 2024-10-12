import boto3

class DynamoDBOperations:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')

    def insert_item(self, table_name, item):
        try:
            table = self.dynamodb.Table(table_name)
            table.put_item(Item=item)
        except Exception as e:
            raise Exception(f"Error inserting item: {str(e)}")

    def update_item(self, table_name, key, update_expression, expression_attributes):
        try:
            table = self.dynamodb.Table(table_name)
            table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attributes
            )
        except Exception as e:
            raise Exception(f"Error updating item: {str(e)}")

    def delete_item(self, table_name, key):
        try:
            table = self.dynamodb.Table(table_name)
            table.delete_item(Key=key)
        except Exception as e:
            raise Exception(f"Error deleting item: {str(e)}")

    def read_item(self, table_name, key):
        try:
            table = self.dynamodb.Table(table_name)
            response = table.get_item(Key=key)
            return response.get('Item', None)
        except Exception as e:
            raise Exception(f"Error reading item: {str(e)}")
