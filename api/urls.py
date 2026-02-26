# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    ProjectViewSet,
    TaskViewSet,
    ActivityViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'projects',   ProjectViewSet,  basename='project')
router.register(r'tasks',      TaskViewSet,     basename='task')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'users',      UserViewSet,     basename='user')

urlpatterns = [
    # Token endpoint: POST {"username": "...", "password": "..."} → {"token": "..."}
    path('auth/token/', obtain_auth_token, name='api_token_auth'),

    # All router-generated URLs
    path('', include(router.urls)),

    # DRF browsable API login (for the HTML browser interface)
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
