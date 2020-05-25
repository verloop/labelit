from django.shortcuts import render, redirect, get_object_or_404
from mainapp.models import Project, ProjectAnnotators
from mainapp.forms import ProjectForm

import os
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_project(request):
    user = request.user
    if user.is_annotator:
        text = "only admin and managers can create projects"
        return render(request, 'manage_projects/not_allowed.html', {'text':text})
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = user
            project.save()
            return redirect('projects_list')
    else:
        form = ProjectForm()
    return render(request, 'manage_projects/create.html', {'form': form})


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

    return render(request, 'manage_projects/list.html', {'projects' : projects, 'user' : user})


def delete_view(request, id):
    user = request.user
    project = Project.objects.get(pk=id)
    if user.is_annotator:
        text = "only admin and managers can delete projects"
        return render(request, 'manage_projects/not_allowed.html', {'text':text})

    obj = get_object_or_404(Project, id = id) 

    if request.method =="POST": 
        obj.delete()
        return redirect('projects_list')
  
    return render(request, "manage_projects/delete.html", {'project':project})