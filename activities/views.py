# activity/views.py
from django.shortcuts import render
from .models import ActivityLog

def activity_feed(request):
    logs = ActivityLog.objects.all()[:200]
    return render(request, 'activities/feed.html', {'logs': logs})
