import boto3

class S3BucketOperations:
    def __init__(self):
        self.s3 = boto3.client('s3')

    def get_object(self, bucket_name, object_key, version_id=None):
        try:
            params = {'Bucket': bucket_name, 'Key': object_key}
            if version_id:
                params['VersionId'] = version_id
            return self.s3.get_object(**params)
        except Exception as e:
            raise Exception(f"Error getting object: {str(e)}")

    def put_object(self, bucket_name, object_key, body):
        try:
            self.s3.put_object(Bucket=bucket_name, Key=object_key, Body=body)
        except Exception as e:
            raise Exception(f"Error putting object: {str(e)}")

    def delete_object(self, bucket_name, object_key, version_id=None):
        try:
            params = {'Bucket': bucket_name, 'Key': object_key}
            if version_id:
                params['VersionId'] = version_id
            self.s3.delete_object(**params)
        except Exception as e:
            raise Exception(f"Error deleting object: {str(e)}")
