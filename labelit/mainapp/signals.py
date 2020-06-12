from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from mainapp.models import Project
from mainapp.jobs import scheduler, manage_project_servers, delete_project_data

@receiver(post_save, sender=Project)
def new_project(sender, instance, created, **kwargs):
    if created:
        # Start project server
        projects_to_start = [instance]
        scheduler.add_job(manage_project_servers, args=[projects_to_start])

@receiver(pre_delete, sender=Project)
def delete_project(sender, instance, using, **kwargs):
    # Stop project server and delete project data
    scheduler.add_job(delete_project_data, args=[instance])
