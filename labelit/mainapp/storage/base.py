from pathlib import Path
from .exceptions import PathExistsException

class StorageHandler():
    def __init__(self):
        """Storage Handler initialization"""
        pass

    def create_dir(self, path):
        path_obj = Path(path)
        if not path_obj.exists():
            path_obj.mkdir(parents=True)
        elif not path_obj.isdir():
            raise PathExistsException(f"Path {path} is a file")

    def download(self):
        """Function for downloading from remote storage"""
        pass

    def upload(self):
        """Function for uploading to remote storage"""
        pass
