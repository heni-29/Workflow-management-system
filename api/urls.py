# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

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
    # JWT endpoints
    # POST {"username": "...", "password": "..."} → {"access": "...", "refresh": "..."}
    path('auth/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),   name='token_refresh'),
    path('auth/token/verify/',  TokenVerifyView.as_view(),    name='token_verify'),

    # All router-generated URLs
    path('', include(router.urls)),

    # DRF browsable API login (for the HTML browser interface)
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
