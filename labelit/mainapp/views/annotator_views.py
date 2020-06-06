from django.shortcuts import render, redirect, get_object_or_404
from mainapp.models import Project, ProjectAnnotators, User
from mainapp.forms import AnnotatorSelectForm
from django.contrib import messages

import os
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def manage_annotators(request, name):
    user = request.user
    if user.is_annotator:
        error = ErrorMessage(header="Access denied", message="Only admin and managers can add/remove annotators")
        return render(request, 'error.html', {'error':error})
    else:
        project = Project.objects.get(name=name)
        annotator_assigned = ProjectAnnotators.objects.filter(project=project).values_list('annotator', flat=True)
        annotators_not_assigned = User.objects.filter(staff_type=User.StaffRole.ANNOTATOR).exclude(id__in=annotator_assigned)
        annotator_assigned = User.objects.filter(staff_type=User.StaffRole.ANNOTATOR).filter(id__in=annotator_assigned)
        if request.method == "POST":
            form = AnnotatorSelectForm(request.POST, annotator_assigned=annotator_assigned, annotators_not_assigned=annotators_not_assigned)
            if form.is_valid():
                annotators_to_remove = form.cleaned_data['annotators_to_remove']
                annotators_to_add = form.cleaned_data['annotators_to_add']

                for annotator in annotators_to_remove:
                    current_mapping = ProjectAnnotators.objects.filter(
                        project=project, 
                        annotator=annotator
                    )
                    current_mapping.delete()


                for annotator in annotators_to_add:
                    new_mapping = ProjectAnnotators(
                        project = project,
                        annotator = annotator
                    )
                    new_mapping.save()
        form = AnnotatorSelectForm(annotator_assigned=annotator_assigned, annotators_not_assigned=annotators_not_assigned)
        return render(request, 'annotator/list_annotators.html', {'form': form})
