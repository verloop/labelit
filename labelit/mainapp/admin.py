from django.contrib import admin

from mainapp.models import Project, ProjectAnnotators

# Register your models here.
admin.site.register(Project)
admin.site.register(ProjectAnnotators)
