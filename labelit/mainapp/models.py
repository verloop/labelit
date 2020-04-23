from django.db import models
from django.core import validators
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from labelit.settings import BASE_DIR


STATUS_CHOICES = (
    (1, ("Initialized")),
    (2, ("Started")),
    (3, ("Failed")),
    (4, ("Completed")),
)

gs_regex = r"gs:\/\/(([a-zA-Z0-9_+.-]+)(\/))+([a-zA-Z0-9_+.-]+)"
# Create your models here.
class Project(models.Model):
    """Model for projects"""

    # Name of project
    name = models.CharField(unique=True, max_length=20)
    # storage bucket path to dataset
    dataset_path = models.CharField(validators=[validators.RegexValidator(regex=r"data/")], max_length=500)
    # xml config
    config = models.TextField()
    # Manager
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    # Project status
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    # Server PID
    server_pid = models.IntegerField(default=0)
    # Server port
    server_port = models.IntegerField(default=0)


import os
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
def get_label_studio_cmd(path_to_dataset, label_config_path, port):
    command_template = "python {} start-multi-session --root-dir={} --input-path={} -l {} -p {} --input-format text"
    server_file = os.path.join(BASE_DIR, "flaskapp/server.py")
    command = command_template.format(server_file, projects_root_dir, path_to_dataset, label_config_path, port)
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
