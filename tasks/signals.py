# tasks/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from activities.models import ActivityLog

@receiver(post_save, sender=Task)
def log_task_change(sender, instance, created, **kwargs):
    verb = 'created_task' if created else 'updated_task'
    ActivityLog.objects.create(
        user=instance.reporter or instance.assignee,
        verb=verb,
        target_type='Task',
        target_id=instance.id,
        detail={
            'title': instance.title,
            'status': instance.status,
            'assignee_id': instance.assignee_id,
            'project_id': instance.project_id,
        }
    )
