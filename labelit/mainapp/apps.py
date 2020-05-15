from django.apps import AppConfig

import sys


class MainappConfig(AppConfig):
    name = 'mainapp'

    def ready(self):
        if ('labelit.wsgi' not in sys.argv and 'runserver' not in sys.argv):
            return True
        # you must import your modules here
        # to avoid AppRegistryNotReady exception
        from .models import startup_run
        # Start all projects
        startup_run()
