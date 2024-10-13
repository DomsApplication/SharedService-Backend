import boto3
import json

class SecretManager:
    def __init__(self):
        self.client = boto3.client('secretsmanager')

    def get_secret(self, secret_name):
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            if 'SecretString' in response:
                return json.loads(response['SecretString'])
            else:
                raise Exception("Binary secrets not supported.")
        except Exception as e:
            raise Exception(f"Error retrieving secret: {str(e)}")
