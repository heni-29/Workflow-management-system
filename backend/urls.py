# backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('projects.urls')),       # root app
    path('tasks/', include('tasks.urls')),
    path('activities/', include('activities.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('users.urls')),

    # REST API — all endpoints live under /api/
    path('api/', include('api.urls')),
]
