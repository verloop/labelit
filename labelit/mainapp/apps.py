from django.apps import AppConfig

import sys


class MainappConfig(AppConfig):
    name = 'mainapp'

    def ready(self):
        if ('labelit.wsgi' not in sys.argv and 'runserver' not in sys.argv):
            return True
        # Import modules
        from labelit.settings import LABELIT_JOB_CONFIG
        from .jobs import scheduler, manage_project_servers, export_projects
        # Start all projects
        manage_project_servers()
        # Add jobs to scheduler
        scheduler.add_job(manage_project_servers, 'interval', seconds=LABELIT_JOB_CONFIG['project_manager']['interval'])
        scheduler.add_job(export_projects, 'interval', seconds=LABELIT_JOB_CONFIG['exporter']['interval'])
        # Start scheduler
        scheduler.start()
        # Import signals
        import mainapp.signals
