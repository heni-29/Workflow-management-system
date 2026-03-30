# backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # REST API — all endpoints live under /api/
    path('api/', include('api.urls')),
]
