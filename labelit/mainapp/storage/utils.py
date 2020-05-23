from .config import storage_prefex_config
from .exceptions import StorageNotSupported

def get_storage_type(storage_path):
    """Get storage type for a storage path (local and supported remote storages)"""
    for storage_type in storage_prefex_config:
        if storage_path.startswith(storage_prefex_config[storage_type]):
            return storage_type
    raise StorageNotSupported("Storage path type not supported")

def split_bucket_path(storage_path):
    """Splits input remote storage path to bucket name and data path"""
    storage_type = get_storage_type(storage_path)
    storage_prefix = storage_prefex_config[storage_type]
    cleaned_path = storage_path[len(storage_prefix):]
    if cleaned_path == '':
        raise InvalidStoragePath(f"Not valid {storage_type} storage path")
    split_path = cleaned_path.split('/', 1)
    if len(split_path) == 1:
        # Root bucket path given
        split_path.append('')
    return split_path[0], split_path[1]
