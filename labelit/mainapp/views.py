from django.shortcuts import render
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from revproxy.views import ProxyView
from mainapp.models import Project

import os
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LSProxyView(ProxyView):
    def get_request_headers(self, *args, **kwargs):
        """Override header setup function to add user, project as header"""
        # Call super to get default headers
        headers = super(LSProxyView, self).get_request_headers()
        # Add new headers
        headers['LABELIT_USER'] = self.request.user.username
        headers['LABELIT_PROJECT'] = self.project_name
        return headers

    def dispatch(self, request, *args, **kwargs):
        """Set upstream Host and port by getting value stored
         in model for the project"""
        self._upstream = 'http://127.0.0.1'
        project = kwargs['project']
        logger.debug(f"Project {project}")
        try:
            project_obj = Project.objects.get(name=project)
        except:
            error = {'message': 'Project not found!'}
            return render(request, 'error.html', {'errors' : [error]})
        if project_obj.status == Project.Status.ACTIVE:
            project_cache = cache.get(str(project_obj.id))
            if not project_cache:
                error = {'message': 'Project not loaded yet!'}
                return render(request, 'error.html', {'errors' : [error]})
            if project_cache['fail_flag']:
                error = {'message': 'Failure while loading project, contact admin.'}
                return render(request, 'error.html', {'errors' : [error]})
            self.project_name = project
            self._upstream += f":{project_cache['port']}"
            del kwargs['project']
            logger.debug(f"Calling {self._upstream}")
            return super().dispatch(request, *args, **kwargs)
        elif project_obj.status == Project.Status.INITIALIZED:
            error = {'message': 'Project not yet active.'}
            return render(request, 'error.html', {'errors' : [error]})
        elif project_obj.status == Project.Status.COMPLETED:
            error = {'message': 'Project has been marked as completed by manager.'}
            return render(request, 'error.html', {'errors' : [error]})
        elif project_obj.status == Project.Status.INACTIVE:
            error = {'message': 'Oops! Project is in inactive state.'}
            return render(request, 'error.html', {'errors' : [error]})
        else:
            error = {'message': 'Unknown state for project.'}
            return render(request, 'error.html', {'errors' : [error]})

@login_required
def projects_list(request):
    """List all projects"""
    projects = Project.objects.all()
    return render(request, 'list_projects.html', {'projects' : projects})
