from socket import socket
import subprocess
import time

from labelit.settings import BASE_DIR_PATH, LABELIT_DIRS

class ErrorMessage():
    """Base class for labelit error messages"""
    def __init__(self, header="Error", message="Error occured", description=""):
        self.header = header
        self.message = message
        self.description = description

def get_random_port():
    """Gets random available port"""
    with socket() as s:
        s.bind(('',0))
        return s.getsockname()[1]

def get_label_studio_cmd(path_to_dataset, dataset_format, label_config_path, port):
    """Returns command to run label studio with given config"""
    command_template = "python {} start-multi-session --root-dir={} --input-path={} --input-format {} --sampling sequential -l {} -p {}"
    server_file = BASE_DIR_PATH / "flaskapp" / "server.py"
    command = command_template.format(server_file, LABELIT_DIRS['projects'], path_to_dataset, dataset_format, label_config_path, port)
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
    config_file_path = LABELIT_DIRS['configs'] / project_name
    with open(config_file_path, 'w') as f:
        f.write(data)
    return config_file_path
