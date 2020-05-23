import psutil, os

from label_studio_converter import Converter
from apscheduler.schedulers.background import BackgroundScheduler

from django.core.cache import cache
from labelit.settings import LABELIT_CONFIG_DIR, LABELIT_PROJECTS_DIR, LABELIT_EXPORT_DIR, LABELIT_TEMP_DIR
from .models import Project, ProjectAnnotators
from .utils import get_random_port, save_config_file, get_label_studio_cmd, start_tool_server
from .storage.utils import get_storage_type
from .storage.exceptions import StorageException


class ProjectNotRunning(Exception):
    """Project server is not running"""

def set_project_cache(project_id, server_pid, server_port, fail_flag):
    project_cache = {'pid': server_pid, 'port': server_port, 'fail_flag': fail_flag}
    cache.set(project_id, project_cache, None)

# Define jobs
def manage_project_servers():
    """Manages Label studio servers for all projects
    Checks status of projects and starts label studio server if it's not running already.
    Sets project cache with server PID and port along with failure flag to mark failures
    while starting servers.
    """
    # Get all projects
    projects = Project.objects.all()
    for project in projects:
        if project.status in [Project.Status.INITIALIZED, Project.Status.ACTIVE]:
            try:
                project_cache = cache.get(str(project.id))
                if not project_cache:
                    raise ProjectNotRunning("Project not found in cache!")
                server_process = psutil.Process(project_cache['pid'])
                server_listen_connections = [connection for connection in server_process.connections() if connection.status == psutil.CONN_LISTEN]
                f=0
                for connection in server_listen_connections:
                    if connection.laddr.port == project_cache['port']:
                        f=1
                if f==1:
                    print(f"Project {project.name} already running pid {project_cache['pid']} port {project_cache['port']}")
                else:
                    raise ProjectNotRunning("Project not running!")
            except ProjectNotRunning:
                print(f"Starting project {project.name}")
                server_port = get_random_port()
                project_id = str(project.id)
                try:
                    project_storage_path_type = get_storage_type(project.dataset_path)
                except StorageException:
                    set_project_cache(project_id, None, None, True)
                    continue
                if project_storage_path_type == 'local':
                    project_local_storage = project.dataset_path
                else:
                    project_local_storage = os.path.join(LABELIT_TEMP_DIR, project.name)
                if project.status == Project.Status.INITIALIZED:
                    label_config_file = save_config_file(project.name, project.config)
                    try:
                        if project_storage_path_type == 'gs':
                            from .storage.gs import GoogleStorageHandler
                            storage_obj = GoogleStorageHandler(project='verloop-dev')
                            storage_obj.download(project.dataset_path, project_local_storage)
                    except StorageException:
                        print("Failure while downloading dataset.")
                        set_project_cache(project_id, None, None, True)
                        # Go to next project
                        continue
                else:
                    label_config_file = os.path.join(LABELIT_CONFIG_DIR, project.name)
                command = get_label_studio_cmd(
                            project_local_storage,
                            project.dataset_format,
                            label_config_file,
                            server_port)
                try:
                    server_pid = start_tool_server(command)
                except:
                    print("Failure while starting label studio server.")
                    set_project_cache(project_id, None, None, True)
                    # Go to next project
                    continue

                if project.status == Project.Status.INITIALIZED:
                    project.status = Project.Status.ACTIVE
                    project.save()

                set_project_cache(project_id, server_pid, server_port, False)

        elif project.status == Project.Status.COMPLETED:
            ## Do something
            pass

def export_projects():
    """Exports labelled data for all export enabled projects using Label Studio converter"""
    # Get all projects
    projects = Project.objects.all()
    for project in projects:
        if project.status == Project.Status.ACTIVE and project.export_format != Project.ExportFormat.NONE:
            print(f"Exporting project {project.name}")
            project_annotators = ProjectAnnotators.objects.filter(project=project)
            print(project_annotators)
            for project_annotator in project_annotators:
                annotator = project_annotator.annotator
                annotator_dir = os.path.join(LABELIT_PROJECTS_DIR, annotator.username, project.name)
                print(annotator_dir)
                label_config_file = os.path.join(annotator_dir, 'config.xml')
                print(label_config_file)
                if os.path.exists(label_config_file):
                    c = Converter(label_config_file)
                    completions_dir = os.path.join(annotator_dir, 'completions/')
                    output_path = os.path.join(LABELIT_EXPORT_DIR, project.name, annotator.username)
                    if project.export_format == Project.ExportFormat.JSON:
                        c.convert_to_json(completions_dir, output_path)
                    elif project.export_format == Project.ExportFormat.CSV:
                        c.convert_to_csv(completions_dir, output_path, sep=',')
                    elif project.export_format == Project.ExportFormat.TSV:
                        c.convert_to_csv(completions_dir, output_path, sep='\t')
                    elif project.export_format == Project.ExportFormat.CONLL:
                        c.convert_to_conll2003(completions_dir, output_path)
                    else:
                        print("Not supported format")


# Init scheduler
scheduler = BackgroundScheduler()
