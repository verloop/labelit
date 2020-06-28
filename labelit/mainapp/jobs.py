import psutil, logging
from shutil import rmtree

from label_studio_converter import Converter
from apscheduler.schedulers.background import BackgroundScheduler

from django.core.cache import cache
from labelit.settings import LABELIT_DIRS, LABELIT_REMOTE_STORAGE_DOWNLOAD_CONFIG, LABELIT_REMOTE_STORAGE_UPLOAD_CONFIG
from .models import Project, ProjectAnnotators
from .utils import get_random_port, save_config_file, get_label_studio_cmd, start_tool_server
from .storage.utils import get_storage_type
from .storage.exceptions import StorageException

logger = logging.getLogger(__name__)

class ProjectNotRunning(Exception):
    """Project server is not running"""

def set_project_cache(project_id, server_pid, server_port, fail_flag):
    project_cache = {'pid': server_pid, 'port': server_port, 'fail_flag': fail_flag}
    cache.set(project_id, project_cache, None)

# Define jobs
def manage_project_servers(projects=None):
    """Manages Label studio servers for all projects
    Checks status of projects and starts label studio server if it's not running already.
    Sets project cache with server PID and port along with failure flag to mark failures
    while starting servers.
    """
    if not projects:
        # Get all projects
        projects = Project.objects.all()
    for project in projects:
        if project.status in [Project.Status.INITIALIZED, Project.Status.ACTIVE]:
            try:
                project_cache = cache.get(str(project.id))
                if not project_cache:
                    raise ProjectNotRunning("Project not found in cache!")
                try:
                    server_process = psutil.Process(project_cache['pid'])
                except:
                    raise ProjectNotRunning(f"Project process with PID {project_cache['pid']} not running")
                server_listen_connections = [connection for connection in server_process.connections() \
                                            if (connection.status == psutil.CONN_LISTEN \
                                            and connection.laddr.port == project_cache['port'])]
                if server_listen_connections:
                    logger.debug(f"Project {project.name} already running pid {project_cache['pid']} port {project_cache['port']}")
                else:
                    raise ProjectNotRunning("Project not running!")
            except ProjectNotRunning as e:
                logger.info(e)
                logger.info(f"Starting project {project.name}")
                server_port = get_random_port()
                project_id = str(project.id)
                try:
                    project_storage_path_type = get_storage_type(project.dataset_path)
                except StorageException:
                    logger.exception("Exception while fetching storage type")
                    set_project_cache(project_id, None, None, True)
                    continue
                if project_storage_path_type == 'local':
                    project_local_storage = project.dataset_path
                else:
                    project_local_storage = LABELIT_DIRS['temp'] / project.name
                if project.status == Project.Status.INITIALIZED:
                    label_config_file = save_config_file(project.name, project.config)
                    try:
                        if project_storage_path_type == 'gs':
                            from .storage.gs import GoogleStorageHandler
                            gs_project = LABELIT_REMOTE_STORAGE_DOWNLOAD_CONFIG['gs']['project']
                            storage_obj = GoogleStorageHandler(project=gs_project)
                            storage_obj.download(project.dataset_path, project_local_storage)
                        elif project_storage_path_type == 's3':
                            from .storage.s3 import S3StorageHandler
                            s3_region = LABELIT_REMOTE_STORAGE_DOWNLOAD_CONFIG['s3']['region']
                            storage_obj = S3StorageHandler(region=s3_region)
                            storage_obj.download(project.dataset_path, project_local_storage)

                    except StorageException:
                        logger.exception("Failure while downloading dataset.")
                        set_project_cache(project_id, None, None, True)
                        # Go to next project
                        continue
                else:
                    label_config_file = LABELIT_DIRS['configs'] / project.name
                command = get_label_studio_cmd(
                            project_local_storage,
                            project.dataset_format,
                            label_config_file,
                            server_port)
                try:
                    server_pid = start_tool_server(command)
                except:
                    logger.exception("Failure while starting label studio server.")
                    set_project_cache(project_id, None, None, True)
                    # Go to next project
                    continue

                if project.status == Project.Status.INITIALIZED:
                    project.status = Project.Status.ACTIVE
                    project.save()

                set_project_cache(project_id, server_pid, server_port, False)
                logger.debug(f"Server cache set for project {project_id}")
        elif project.status == Project.Status.COMPLETED:
            ## Do something
            pass

def export_projects():
    """Exports labelled data for all export enabled projects using Label Studio converter"""
    # Get all projects
    projects = Project.objects.all()
    for project in projects:
        storage_type = None
        if not project.remote_export=="None":
            # Declare a storage object which will be used to upload files later
            storage_type = get_storage_type(project.remote_export)
            if storage_type == "gs":
                from .storage.gs import GoogleStorageHandler
                gs_project = LABELIT_REMOTE_STORAGE_UPLOAD_CONFIG['gs']['project']
                storage_obj =  GoogleStorageHandler(project = gs_project)
            elif storage_type == "s3":
                from .storage.s3 import S3StorageHandler
                s3_region = LABELIT_REMOTE_STORAGE_UPLOAD_CONFIG['s3']['region']
                storage_obj = S3StorageHandler(region=s3_region)

        if project.status == Project.Status.ACTIVE and project.export_format != Project.ExportFormat.NONE:
            logger.info(f"Exporting project {project.name}")
            output_paths = []
            project_annotators = ProjectAnnotators.objects.filter(project=project)
            for project_annotator in project_annotators:
                annotator = project_annotator.annotator
                annotator_dir = LABELIT_DIRS['projects'] / annotator.username / project.name
                label_config_file = annotator_dir / 'config.xml'
                if label_config_file.exists():
                    c = Converter(str(label_config_file))
                    completions_dir = annotator_dir / 'completions/'
                    output_path = LABELIT_DIRS['exports'] / project.name / annotator.username
                    logger.debug(f"Exporting completions for annotator {annotator.username}, project {project.name}")
                    if project.export_format == Project.ExportFormat.JSON:
                        c.convert_to_json(completions_dir, output_path)
                    elif project.export_format == Project.ExportFormat.CSV:
                        c.convert_to_csv(completions_dir, output_path, sep=',')
                    elif project.export_format == Project.ExportFormat.TSV:
                        c.convert_to_csv(completions_dir, output_path, sep='\t')
                    elif project.export_format == Project.ExportFormat.CONLL:
                        c.convert_to_conll2003(completions_dir, output_path)
                    else:
                        logger.debug(f"Export format {project.export_format} not supported for project {project.name}")
                        continue
                    output_paths.append(output_path)
                    # Both GS and S3 util have the same upload function which take the same set of parameters to
                    # upload a file to the bucket.
                    # The above declared `storage_obj` is used to upload.    
                    if storage_type:
                        file_to_upload = list(x for x in output_path.iterdir() if x.is_file())[0]
                        storage_path = f"{project.name}/{annotator.username}/{str(file_to_upload).split('/')[-1]}"
                        storage_obj.upload(project.remote_export, storage_path, file_to_upload)
                    

def stop_project_servers(projects=None):
    """Stops running Label studio servers"""
    if not projects:
        projects = Project.objects.all()
    for project in projects:
        try:
            project_cache = cache.get(str(project.id))
            if not project_cache:
                raise ProjectNotRunning("Project not found in cache!")
            try:
                server_process = psutil.Process(project_cache['pid'])
            except:
                raise ProjectNotRunning("Project process with PID")
            # Terminate server process
            server_process.terminate()
        except ProjectNotRunning as e:
            logger.error(e)
            pass

def delete_project_data(project=None):
    """Deletes a given project including stored data"""
    logger.info(f"Stopping server and deleting data for project {project.name} with ID {project.id}")
    # Stop project server
    try:
        stop_project_servers([project])
    except Exception as e:
        logger.error(e)
        # Exception while stopping project server, pass for now.
        pass
    try:
        # Delete project data of annotators
        project_data_dir = LABELIT_DIRS['projects']
        for annotator_dir in project_data_dir.glob('*'):
            if annotator_dir.is_dir():
                annotator_project_dir = annotator_dir / project.name
                if annotator_project_dir.exists():
                    rmtree(annotator_project_dir)
        # Delete exported data
        project_export_dir = LABELIT_DIRS['exports'] / project.name
        if project_export_dir.exists():
            rmtree(project_export_dir)
    except Exception as e:
        logger.error(e)
        # Exception while deleting directories, handle cases in future release
        pass
    logger.info(f"Deleted project {project.name} with ID {project.id}")

# Init scheduler
scheduler = BackgroundScheduler()
