from django.shortcuts import render, get_object_or_404
from mainapp.models import Project, ProjectAnnotators, User
from mainapp.forms import AnnotatorSelectForm

import os
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def manage_annotators(request, name):
    """View to manage annotators for projects"""
    user = request.user
    if user.is_annotator:
        error = ErrorMessage(header="Access denied", message="Only admin and managers can add/remove annotators")
        return render(request, 'error.html', {'error':error})
    else:
        project = Project.objects.get(name=name)
        annotators_assigned = ProjectAnnotators.objects.filter(project=project).values_list('annotator', flat=True)
        if request.method == "POST":
            form = AnnotatorSelectForm(request.POST)
            if form.is_valid():
                annotators = form.cleaned_data['annotators']
                annotators_ids = [annotator.id for annotator in annotators]
                annotators_to_add = [annotator for annotator in annotators if annotator.id not in annotators_assigned]
                annotators_to_remove_ids = set(annotators_assigned) - set(annotators_ids)
                if annotators_to_remove_ids:
                    annotators_to_remove = User.objects.filter(id__in=annotators_to_remove_ids)
                    # Update mapping table
                    for annotator in annotators_to_remove:
                        mapping_to_remove = ProjectAnnotators.objects.filter(
                            project = project,
                            annotator = annotator
                        )
                        mapping_to_remove.delete()

                for annotator in annotators_to_add:
                    mapping_to_add = ProjectAnnotators(
                        project = project,
                        annotator = annotator
                    )
                    mapping_to_add.save()
                # Show new set of annotators as initial
                annotators_assigned = annotators_ids
        form = AnnotatorSelectForm(initial={'annotators': annotators_assigned})
        return render(request, 'projects/manage_annotators.html', {'form': form, 'project': project})
