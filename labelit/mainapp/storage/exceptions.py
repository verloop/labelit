
class StorageException(Exception):
    """Base class for all storage exceptions"""

class PathExistsException(StorageException):
    """The given path already exists"""

class StorageNotSupported(StorageException):
    """Storage type not supported"""

class InvalidStoragePath(StorageException):
    """Invalid storage path given"""
