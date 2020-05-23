from django.apps import AppConfig

import sys


class MainappConfig(AppConfig):
    name = 'mainapp'

    def ready(self):
        if ('labelit.wsgi' not in sys.argv and 'runserver' not in sys.argv):
            return True
        # Import modules
        from .jobs import scheduler, manage_project_servers, export_projects
        # Start all projects
        manage_project_servers()
        # Add jobs to scheduler
        scheduler.add_job(manage_project_servers, 'interval', seconds=150)
        scheduler.add_job(export_projects, 'interval', seconds=300)
        # Start scheduler
        scheduler.start()
