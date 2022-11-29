from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from mainapp.validators import validate_dataset_path, validate_label_config, validate_remote_path

class User(AbstractUser):
    class StaffRole(models.IntegerChoices):
        ANNOTATOR = 1, _("Annotator")
        MANAGER = 2, _("Manager")
        ADMIN = 3, _("Admin")

    staff_type = models.IntegerField(choices=StaffRole.choices,default=StaffRole.ADMIN, verbose_name="Staff Role Level")

    @property
    def is_annotator(self):
        if self.staff_type == self.StaffRole.ANNOTATOR:
            return True
        return False

    @property
    def is_manager(self):
        if self.staff_type == self.StaffRole.MANAGER:
            return True
        return False

    @property
    def is_admin(self):
        if self.staff_type == self.StaffRole.ADMIN:
            return True
        return False


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
    name = models.CharField(unique=True, max_length=20, help_text="Name of your project", verbose_name="Project Name")
    # Dataset type
    dataset_format = models.CharField(choices=DatasetFormat.choices, max_length=20, default=DatasetFormat.TEXT_DIR, help_text="Format of your dataset", verbose_name="Dataset Format")
    # storage path to dataset
    dataset_path = models.CharField(validators=[validate_dataset_path], max_length=500, help_text="Path where dataset is stored", verbose_name="Dataset Path")
    # xml config
    config = models.TextField(validators=[validate_label_config], help_text="Label studio config, you can find templates and test the config <a target='_blank' rel='noopener noreferrer' href='https://labelstud.io/playground/'>here</a>", verbose_name="Label Studio XML")
    # Manager
    manager = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, help_text="Manager of this project")
    # Project status
    status = models.IntegerField(choices=Status.choices, default=Status.INITIALIZED, help_text="Status of project")
    # Export format
    export_format = models.IntegerField(choices=ExportFormat.choices, default=ExportFormat.NONE, help_text="Export format for labelled data", verbose_name="Export Format")
    # Remote Export Path
    remote_export = models.CharField(validators=[validate_remote_path], default="None", max_length=500, help_text="Remote export path (GS or S3)", verbose_name="Remote Storage")


class ProjectAnnotators(models.Model):
    """Model mapping annotators for different projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    annotator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
