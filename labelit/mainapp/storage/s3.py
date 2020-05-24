import os
from .base import StorageHandler
from .utils import split_bucket_path

try:
    import boto3
except ImportError:
    raise Exception("Couldn't import AWS S3 library")

class S3StorageHandler(StorageHandler):
    def __init__(self, region=None):
        if region:
            self.storage_client = boto3.client('s3', region)
        else:
            self.storage_client = boto3.client('s3')

    def download(self, storage_path, download_path):
        self.create_dir(download_path)
        # Code to download files from bucket to path
        bucket_name, source_object_path = split_bucket_path(storage_path)
        # List all objects in the path
        list_objects_result = self.storage_client.list_objects_v2(Bucket=bucket_name, Prefix=source_object_path)
        objects = list_objects_result['Contents']
        # Download all objects to our local directory
        for object in objects:
            if object['Key'].endswith('/'):
                # Skipping directories
                continue
            # Handle files in sub-directories
            cleaned_object_name = object['Key'].replace('/', '_')
            destination_file_name = os.path.join(download_path, cleaned_object_name)
            self.storage_client.download_file(bucket_name, object['Key'], destination_file_name)
