from django.shortcuts import render, redirect, get_object_or_404
from mainapp.models import Project, ProjectAnnotators
from mainapp.forms import ProjectForm
from mainapp.utils import ErrorMessage

import os
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_project(request):
    """View to create new project"""
    user = request.user
    if user.is_annotator:
        error = ErrorMessage(header="Access denied", message="Only admin and managers can create projects")
        return render(request, 'error.html', {'error':error})
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = user
            project.save()
            return redirect('projects_list')
    else:
        form = ProjectForm()
    return render(request, 'projects/create.html', {'form': form})


def list_projects(request):
    """List all projects"""
    user = request.user
    if user.is_manager:
        projects = Project.objects.filter(manager = request.user)
    elif user.is_annotator:
        project_names = ProjectAnnotators.objects.values_list('project', flat=True).filter(annotator = user)
        projects = Project.objects.filter(pk__in=project_names)
    elif user.is_admin:
        projects = Project.objects.all()

    return render(request, 'projects/list.html', {'projects' : projects, 'user' : user})


def delete_view(request):
    """View to delete an existing project"""
    user = request.user
    if request.method =="POST":
        id = request.POST.get('id', None)
        if id:
            project = get_object_or_404(Project, id=id)
            if user.is_annotator or (user.is_manager and project.manager.username != user):
                error = ErrorMessage(header="Access denied", message="Only admin and managers can delete projects")
                return render(request, 'error.html', {'error':error})
            project.delete()
            return redirect('projects_list')
        else:
            error = ErrorMessage(header="Delete project", message="Please provide valid project ID")
            return render(request, 'error.html', {'error':error})
    else:
        error = ErrorMessage(header="Method not supported", message="This request method is not supported!")
        return render(request, 'error.html', {'error':error})
