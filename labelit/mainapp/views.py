from django.shortcuts import render
from revproxy.views import ProxyView
from mainapp.models import Project

import os
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from django.contrib.auth.decorators import login_required

# Create your views here.
class LSProxyView(ProxyView):
    def get_request_headers(self, *args, **kwargs):
        #project_name = kwargs['project']
        # Call super to get default headers
        headers = super(LSProxyView, self).get_request_headers()
        # Add new header
        headers['VER_USER'] = self.request.user.username
        headers['VER_PROJECT'] = self.project_name
        return headers

    """
    def _created_proxy_response(self, request, path):
        import urllib3
        request_payload = request.body

        logger.info("Request headers: %s", self.request_headers)

        path = self.get_quoted_path(path)

        request_url = self.get_upstream(path) + path
        logger.info("Request URL: %s", request_url)

        if request.GET:
            request_url += '?' + self.get_encoded_query_params()
            logger.info("Request URL: %s", request_url)

        try:
            proxy_response = self.http.urlopen(request.method,
                                               request_url,
                                               redirect=False,
                                               retries=self.retries,
                                               headers=self.request_headers,
                                               body=request_payload,
                                               decode_content=False,
                                               preload_content=False)
            logger.info("Proxy response header: %s",
                           proxy_response.getheaders())
        except urllib3.exceptions.HTTPError as error:
            logger.info(error)
            raise

        return proxy_response
    """

    def dispatch(self, request, *args, **kwargs):
        self._upstream = 'http://127.0.0.1'
        project = kwargs['project']
        print(f"Project {project}")
        project_obj = Project.objects.get(name=project)
        self.project_name = project
        self._upstream += f":{project_obj.server_port}"
        del kwargs['project']
        #os.environ['VER_USER'] = request.user.username
        #os.environ['VER_PROJECT'] = self.project_name
        logger.debug(f"Calling {self._upstream}")
        return super().dispatch(request, *args, **kwargs)

@login_required
def projects_list(request):
    projects = Project.objects.all()
    return render(request, 'list_projects.html', {'projects' : projects})
