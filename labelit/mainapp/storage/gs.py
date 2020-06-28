import os
from .base import StorageHandler
from .utils import split_bucket_path
from labelit.settings import LABELIT_DIRS
from pathlib import Path

try:
    from google.cloud import storage
except ImportError:
    raise Exception("Couldn't import Google storage module")

class GoogleStorageHandler(StorageHandler):
    def __init__(self, project=None):
        if project:
            self.storage_client = storage.Client(project=project)
        else:
            self.storage_client = storage.Client()

    def download(self, storage_path, download_path):
        self.create_dir(download_path)
        # Code to download files from bucket to path
        bucket_name, source_blob_path = split_bucket_path(storage_path)
        # List all blobs in the path
        blobs = self.storage_client.list_blobs(bucket_name, prefix=source_blob_path)
        # Download all blobs to our local directory
        for blob in blobs:
            # Handle files in sub-directories
            cleaned_blob_name = blob.name.replace('/', '_')
            destination_file_name = os.path.join(download_path, cleaned_blob_name)
            blob.download_to_filename(destination_file_name)

    def upload(self, bucket_address, bucket_path_of_file, file_to_upload):
        bucket_name, source_blob_path = split_bucket_path(bucket_address)
        if len(source_blob_path) > 0:
            if not source_blob_path.endswith("/"):
                source_blob_path += "/"
            bucket_path_of_file = source_blob_path + bucket_path_of_file
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(bucket_path_of_file)
        blob.upload_from_filename(file_to_upload)
