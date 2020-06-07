import logging
import urllib3

from django.shortcuts import render
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from revproxy.views import ProxyView
from mainapp.models import Project
from mainapp.utils import ErrorMessage
from labelit.settings import LSPROXY_CONNECTION_POOL_COUNT, LSPROXY_CONNECTION_PER_POOL

logger = logging.getLogger(__name__)

class LSProxyView(ProxyView):
    def __init__(self, *args, **kwargs):
        super(LSProxyView, self).__init__(*args, **kwargs)
        self.http = urllib3.PoolManager(num_pools=LSPROXY_CONNECTION_POOL_COUNT, maxsize=LSPROXY_CONNECTION_PER_POOL)

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
            error = ErrorMessage(message='Project not found!')
            return render(request, 'error.html', {'error' : error})
        if project_obj.status == Project.Status.ACTIVE:
            project_cache = cache.get(str(project_obj.id))
            if not project_cache:
                error = ErrorMessage(message='Project not loaded yet!')
                return render(request, 'error.html', {'error' : error})
            if project_cache['fail_flag']:
                error = ErrorMessage(message='Failure while loading project, contact admin.')
                return render(request, 'error.html', {'error' : error})
            # Setup request for proxy
            self.project_name = project
            self._upstream += f":{project_cache['port']}"
            del kwargs['project']
            logger.debug(f"Calling {self._upstream}")
            # Proxy the request
            return super().dispatch(request, *args, **kwargs)
        elif project_obj.status == Project.Status.INITIALIZED:
            error = ErrorMessage(message='Project not yet active.')
            return render(request, 'error.html', {'error' : error})
        elif project_obj.status == Project.Status.COMPLETED:
            error = ErrorMessage(message='Project has been marked as completed by manager.')
            return render(request, 'error.html', {'error' : error})
        elif project_obj.status == Project.Status.INACTIVE:
            error = ErrorMessage(message='Oops! Project is in inactive state.')
            return render(request, 'error.html', {'error' : error})
        else:
            error = ErrorMessage(message='Unknown state for project.')
            return render(request, 'error.html', {'error' : error})
