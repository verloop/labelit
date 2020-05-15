from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from labelit.settings import BASE_DIR
import os


# gs_regex = r"gs:\/\/(([a-zA-Z0-9_+.-]+)(\/))+([a-zA-Z0-9_+.-]+)"

def validate_dataset_path(value):
    """Validates the path for input dataset"""
    if not os.path.isabs(value):
        raise ValidationError(
            _('Enter a valid absolute path!'),
            code='invalid'
        )

# Create your models here.
class Project(models.Model):
    """Model for projects"""
    class DatasetFormat(models.TextChoices):
        TEXT_FILE = "text", _("Text file")
        TEXT_DIR = "text-dir", _("Directory containing text files")
        IMAGE_DIR = "image-dir", _("Directory containing image files")
        AUDIO_DIR = "audio-dir", _("Directory containing audio files")

    class Status(models.IntegerChoices):
        INITIALIZED = 1, _("Initialized")
        STARTED = 2, _("Started")
        FAILED = 3, _("Failed")
        COMPLETED = 4, _("Completed")

    # Name of project
    name = models.CharField(unique=True, max_length=20, help_text="Name of your project")
    # Dataset type
    dataset_format = models.CharField(choices=DatasetFormat.choices, max_length=20, default=DatasetFormat.TEXT_FILE, help_text="Format of your dataset")
    # storage bucket path to dataset
    dataset_path = models.CharField(validators=[validate_dataset_path], max_length=500)
    # xml config
    config = models.TextField()
    # Manager
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    # Project status
    status = models.IntegerField(choices=Status.choices, default=Status.INITIALIZED)
    # Server PID
    server_pid = models.IntegerField(default=0)
    # Server port
    server_port = models.IntegerField(default=0)



temp_config_path = os.path.join(BASE_DIR, 'tmp')
def save_config_file(project_name, data):
    config_file_path = os.path.join(temp_config_path,project_name)
    with open(config_file_path, 'w') as f:
        f.write(data)
    return config_file_path


from socket import socket
def get_random_port():
    with socket() as s:
        s.bind(('',0))
        return s.getsockname()[1]

projects_root_dir = os.path.join(BASE_DIR, 'projects')
def get_label_studio_cmd(path_to_dataset, dataset_format, label_config_path, port):
    command_template = "python {} start-multi-session --root-dir={} --input-path={} --input-format {} --sampling sequential -l {} -p {}"
    server_file = os.path.join(BASE_DIR, "flaskapp/server.py")
    command = command_template.format(server_file, projects_root_dir, path_to_dataset, dataset_format, label_config_path, port)
    return command

import subprocess
import time
def start_tool_server(command):
    p = subprocess.Popen(command.split())
    time.sleep(0.2)
    if p.poll() != None:
        raise ValidationError(f"Starting server failed with return code {p.returncode}")
    return p.pid


# Start all projects
def startup_run():
    projects = Project.objects.all()
    for project in projects:
        server_port = get_random_port()
        label_config_file = os.path.join(temp_config_path, project.name)
        command = get_label_studio_cmd(
                    project.dataset_path,
                    project.dataset_format,
                    label_config_file,
                    server_port)
        server_pid = start_tool_server(command)
        project.server_pid = server_pid
        project.server_port = server_port
        project.status = 2
        project.save()

from django.db.models.signals import post_save
from django.dispatch import receiver
@receiver(post_save, sender=Project)
def run_tool(sender, instance, created, **kwargs):
    if created:
        # Add code to download from bucket to local path here

        # save config to xml file
        label_config_file = save_config_file(instance.name, instance.config)
        server_port = get_random_port()
        command = get_label_studio_cmd(
                instance.dataset_path,
                instance.dataset_format,
                label_config_file,
                server_port)
        server_pid = start_tool_server(command)
        instance.server_pid = server_pid
        instance.server_port = server_port
        # Set project status as started
        instance.status = 2
        instance.save()


class ProjectAnnotators(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    annotator = models.ForeignKey(User, on_delete=models.CASCADE)
