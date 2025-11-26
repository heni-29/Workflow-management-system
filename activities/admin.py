from django.contrib import admin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('verb','user','target_type','target_id','timestamp')
    search_fields = ('verb','detail')
