# activity/models.py
from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    verb = models.CharField(max_length=50)  # e.g., 'created', 'updated'
    target_type = models.CharField(max_length=50, null=True, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    detail = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
