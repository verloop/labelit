from pathlib import Path

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from mainapp.storage.utils import get_storage_type
from label_studio.utils.misc import parse_config

def validate_dataset_path(value):
    """Validates the path for input dataset"""
    try:
        storage_type = get_storage_type(value)
        if storage_type == 'local':
            dataset_path = Path(value)
            if not dataset_path.is_dir():
                raise Exception("Directory doesn't exist")
    except:
        raise ValidationError(
            _('Enter a valid storage path!'),
            code='invalid'
        )

def validate_label_config(config):
    """Validates the label studio config"""
    try:
        parsed_config = parse_config(config)
    except:
        raise ValidationError(
            _('Invalid Label Studio config'),
            code='invalid'
        )

def validate_remote_path(value):
    try:
        storage_type = get_storage_type(value)
        if storage_type == 'local':
            raise Exception("Please enter valid GCP or AWS Format")
    except:
        raise ValidationError(
            _('Enter a valid storage path!'),
            code='invalid'
        )
