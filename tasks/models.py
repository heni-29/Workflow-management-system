# tasks/models.py
from django.db import models
from django.conf import settings
from projects.models import Project

class TaskStatus(models.TextChoices):
    TODO = 'todo', 'To Do'
    IN_PROGRESS = 'in_progress', 'In Progress'
    REVIEW = 'review', 'In Review'
    DONE = 'done', 'Done'

class TaskPriority(models.IntegerChoices):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tasks')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reported_tasks')
    status = models.CharField(max_length=30, choices=TaskStatus.choices, default=TaskStatus.TODO)
    priority = models.IntegerField(choices=TaskPriority.choices, default=TaskPriority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.project})"
