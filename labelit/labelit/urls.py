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
from mainapp.views import LSProxyView, projects_list
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('projects/list', projects_list, name='projects_list'),
    path('api/<str:path>', login_required(LSProxyView.as_view()), {'path': ''}, name='LSAPIView'),
    path('label/<str:project>', login_required(LSProxyView.as_view()), {'path': ''}, name='LSHomeView'),
    path('label/<str:project>/<path:path>', login_required(LSProxyView.as_view()), name='LSView'),
    path('', include('django.contrib.auth.urls')),
]

urlpatterns += staticfiles_urlpatterns()
