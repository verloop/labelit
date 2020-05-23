from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from labelit.settings import BASE_DIR
from label_studio.utils.misc import parse_config
import os

from .storage.utils import get_storage_type


# gs_regex = r"gs:\/\/(([a-zA-Z0-9_+.-]+)(\/))+([a-zA-Z0-9_+.-]+)"

def validate_dataset_path(value):
    """Validates the path for input dataset"""
    try:
        storage_type = get_storage_type(value)
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


class Project(models.Model):
    """Model for projects"""
    class DatasetFormat(models.TextChoices):
        TEXT_DIR = "text-dir", _("Directory containing text files")
        IMAGE_DIR = "image-dir", _("Directory containing image files")
        AUDIO_DIR = "audio-dir", _("Directory containing audio files")

    class ExportFormat(models.IntegerChoices):
        NONE = 1, _("None/ No export")
        JSON = 2, _("JSON")
        CSV = 3, _("CSV")
        TSV = 4, _("TSV")
        CONLL = 5, _("CONLL")

    class Status(models.IntegerChoices):
        INITIALIZED = 1, _("Initialized")
        ACTIVE = 2, _("Active")
        DISABLED = 3, _("Disabled")
        COMPLETED = 4, _("Completed")

    # Name of project
    name = models.CharField(unique=True, max_length=20, help_text="Name of your project")
    # Dataset type
    dataset_format = models.CharField(choices=DatasetFormat.choices, max_length=20, default=DatasetFormat.TEXT_DIR, help_text="Format of your dataset")
    # storage path to dataset
    dataset_path = models.CharField(validators=[validate_dataset_path], max_length=500, help_text="Path where dataset is stored")
    # xml config
    config = models.TextField(validators=[validate_label_config], help_text="Label studio config")
    # Manager
    manager = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Manager of this project")
    # Project status
    status = models.IntegerField(choices=Status.choices, default=Status.INITIALIZED, help_text="Status of project")
    # Export format
    export_format = models.IntegerField(choices=ExportFormat.choices, default=ExportFormat.NONE, help_text="Export format for labelled data")


class ProjectAnnotators(models.Model):
    """Model mapping annotators for different projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    annotator = models.ForeignKey(User, on_delete=models.CASCADE)
