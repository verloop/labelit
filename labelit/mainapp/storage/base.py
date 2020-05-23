import os
from .exceptions import PathExistsException

class StorageHandler():
    def __init__(self):
        """Storage Handler initialization"""
        pass

    def create_dir(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        elif not os.path.isdir(path):
            raise PathExistsException(f"Path {path} is a file")

    def download(self):
        """Function for downloading from remote storage"""
        pass

    def upload(self):
        """Function for uploading to remote storage"""
        pass
