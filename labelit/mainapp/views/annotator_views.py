from django.shortcuts import render, redirect, get_object_or_404
from mainapp.models import Project, ProjectAnnotators, User
from mainapp.forms import AnnotatorSelectForm
from django.contrib import messages


import os
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def add_annotator(request, name):
    user = request.user
    if user.is_annotator:
        text = "only admin and managers can add annotators"
        return render(request, 'manage_projects/not_allowed.html', {'text':text})
    else:
        project = Project.objects.get(name=name)
        # print(project)
        annotator_assigned = ProjectAnnotators.objects.filter(project=project).values_list('annotator', flat=True)
        annotators_not_assigned = User.objects.filter(staff_type=User.StaffRole.ANNOTATOR).exclude(id__in=annotator_assigned)
        if request.method == "POST":
            form = AnnotatorSelectForm(request.POST, queryset=annotators_not_assigned)
            if form.is_valid():
                selected_annotators = form.cleaned_data['annotators'] 
                for annotator in selected_annotators:
                    new_mapping = ProjectAnnotators(
                        project = project,
                        annotator = annotator
                    )
                    new_mapping.save()
        form = AnnotatorSelectForm(queryset=annotators_not_assigned)
        return render(request, 'annotator/list_annotators.html', {'form': form})

def remove_annotator(request, name):
    user = request.user
    if user.is_annotator:
        text = "only admin and managers can remove annotators"
        return render(request, 'manage_projects/not_allowed.html', {'text':text})
    else:
        project = Project.objects.get(name=name)
        annotator_assigned = ProjectAnnotators.objects.filter(project=project).values_list('annotator', flat=True)
        if request.method == "POST":
            form = AnnotatorSelectForm(request.POST, queryset=annotator_assigned)
            if form.is_valid():
                print("In here ~~")
                selected_annotators = form.cleaned_data['annotators'] 
                print(selected_annotators)
        form = AnnotatorSelectForm(queryset=annotator_assigned)
        return render(request, 'annotator/list_annotators.html', {'form': form})