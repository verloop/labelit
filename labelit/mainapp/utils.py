from socket import socket
import subprocess
import time
import os

from labelit.settings import BASE_DIR, LABELIT_PROJECTS_DIR, LABELIT_CONFIG_DIR

def get_random_port():
    """Gets random available port"""
    with socket() as s:
        s.bind(('',0))
        return s.getsockname()[1]


def get_label_studio_cmd(path_to_dataset, dataset_format, label_config_path, port):
    """Returns command to run label studio with given config"""
    command_template = "python {} start-multi-session --root-dir={} --input-path={} --input-format {} --sampling sequential -l {} -p {}"
    server_file = os.path.join(BASE_DIR, "flaskapp/server.py")
    command = command_template.format(server_file, LABELIT_PROJECTS_DIR, path_to_dataset, dataset_format, label_config_path, port)
    return command


def start_tool_server(command):
    """Starts tool server, checks if it's running and return process ID"""
    p = subprocess.Popen(command.split())
    time.sleep(0.2)
    if p.poll() != None:
        raise Exception(f"Starting server failed with return code {p.returncode}")
    return p.pid


def save_config_file(project_name, data):
    """Saves label studio config file"""
    config_file_path = os.path.join(LABELIT_CONFIG_DIR, project_name)
    with open(config_file_path, 'w') as f:
        f.write(data)
    return config_file_path
