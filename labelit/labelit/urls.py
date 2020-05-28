"""labelit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from mainapp.views import LSProxyView, create_project, list_projects, delete_view
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    # Base URL's
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('', login_required(list_projects), name='projects_list_home'),

    # Label Studio API URL's
    path('api/<str:path>', login_required(LSProxyView.as_view()), {'path': ''}, name='LSAPIView'),
    path('label/<str:project>', login_required(LSProxyView.as_view()), {'path': ''}, name='LSHomeView'),
    path('label/<str:project>/<path:path>', login_required(LSProxyView.as_view()), name='LSView'),
    
    # Project Manager URL's
    path('projects/create', login_required(create_project), name='create_project'),
    path('projects/list', login_required(list_projects), name='projects_list'),
    path('projects/<id>/delete', login_required(delete_view), name='delete_project'),
]

urlpatterns += staticfiles_urlpatterns()