from django.shortcuts import render
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
        project_obj = Project.objects.get(name=project)
        self.project_name = project
        self._upstream += f":{project_obj.server_port}"
        del kwargs['project']
        logger.debug(f"Calling {self._upstream}")
        return super().dispatch(request, *args, **kwargs)

@login_required(login_url='/login')
def projects_list(request):
    """List all projects"""
    projects = Project.objects.all()
    return render(request, 'list_projects.html', {'projects' : projects})
