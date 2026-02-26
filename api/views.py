# api/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q

from projects.models import Project
from tasks.models import Task, TaskStatus
from activities.models import ActivityLog

from .serializers import (
    ProjectSerializer,
    TaskSerializer,
    TaskStatusUpdateSerializer,
    ActivityLogSerializer,
    UserSerializer,
)

User = get_user_model()


# ─── Project ViewSet ───────────────────────────────────────────────────────────

class ProjectViewSet(viewsets.ModelViewSet):
    """
    CRUD for projects.

    list   GET  /api/projects/
    create POST /api/projects/
    retrieve GET  /api/projects/{id}/
    update PUT  /api/projects/{id}/
    partial_update PATCH /api/projects/{id}/
    destroy DELETE /api/projects/{id}/
    tasks  GET  /api/projects/{id}/tasks/        <- bonus action
    stats  GET  /api/projects/{id}/stats/        <- bonus action
    """
    serializer_class   = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['name', 'description']
    ordering_fields    = ['name', 'created_at', 'updated_at']
    ordering           = ['-created_at']

    def get_queryset(self):
        qs = Project.objects.prefetch_related('members', 'tasks').select_related('created_by')
        # Optional ?member=<user_id> filter
        member_id = self.request.query_params.get('member')
        if member_id:
            qs = qs.filter(members__id=member_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], url_path='tasks')
    def tasks(self, request, pk=None):
        """GET /api/projects/{id}/tasks/ — all tasks for this project."""
        project = self.get_object()
        tasks   = project.tasks.select_related('assignee', 'reporter')

        # Optional status filter: ?status=todo
        status_param = request.query_params.get('status')
        if status_param:
            tasks = tasks.filter(status=status_param)

        serializer = TaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        """GET /api/projects/{id}/stats/ — task counts per status & priority."""
        project = self.get_object()
        tasks   = project.tasks.all()

        by_status = {}
        for key, label in TaskStatus.choices:
            by_status[key] = {'label': label, 'count': tasks.filter(status=key).count()}

        return Response({
            'project_id': project.id,
            'project_name': project.name,
            'total_tasks': tasks.count(),
            'by_status': by_status,
            'overdue': tasks.filter(
                due_date__lt=__import__('datetime').date.today()
            ).exclude(status=TaskStatus.DONE).count(),
        })


# ─── Task ViewSet ──────────────────────────────────────────────────────────────

class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD for tasks.

    list   GET  /api/tasks/
    create POST /api/tasks/
    retrieve GET  /api/tasks/{id}/
    update PUT  /api/tasks/{id}/
    partial_update PATCH /api/tasks/{id}/
    destroy DELETE /api/tasks/{id}/
    set_status PATCH /api/tasks/{id}/set_status/   <- quick status change
    my_tasks GET  /api/tasks/my/                    <- tasks assigned to me
    """
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'description', 'project__name']
    ordering_fields    = ['created_at', 'updated_at', 'due_date', 'priority', 'status']
    ordering           = ['-created_at']

    def get_queryset(self):
        qs = Task.objects.select_related('project', 'assignee', 'reporter')

        # ?project=<id>
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)

        # ?status=todo|in_progress|review|done
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        # ?priority=1|2|3
        priority_param = self.request.query_params.get('priority')
        if priority_param:
            qs = qs.filter(priority=priority_param)

        # ?assignee=<id>
        assignee_id = self.request.query_params.get('assignee')
        if assignee_id:
            qs = qs.filter(assignee_id=assignee_id)

        # ?overdue=true
        if self.request.query_params.get('overdue') == 'true':
            import datetime
            qs = qs.filter(
                due_date__lt=datetime.date.today()
            ).exclude(status=TaskStatus.DONE)

        return qs

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    @action(detail=True, methods=['patch'], url_path='set_status')
    def set_status(self, request, pk=None):
        """PATCH /api/tasks/{id}/set_status/ — quickly change task status."""
        task = self.get_object()
        ser  = TaskStatusUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        task.status = ser.validated_data['status']
        task.save(update_fields=['status', 'updated_at'])
        return Response(TaskSerializer(task, context={'request': request}).data)

    @action(detail=False, methods=['get'], url_path='my')
    def my_tasks(self, request):
        """GET /api/tasks/my/ — tasks assigned to the current user."""
        tasks = self.get_queryset().filter(assignee=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


# ─── Activity ViewSet ──────────────────────────────────────────────────────────

class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only activity log feed.

    list     GET /api/activities/
    retrieve GET /api/activities/{id}/
    """
    serializer_class   = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [filters.OrderingFilter]
    ordering_fields    = ['timestamp']
    ordering           = ['-timestamp']

    def get_queryset(self):
        qs = ActivityLog.objects.select_related('user')

        # ?target_type=Task
        target_type = self.request.query_params.get('target_type')
        if target_type:
            qs = qs.filter(target_type__iexact=target_type)

        # ?target_id=5
        target_id = self.request.query_params.get('target_id')
        if target_id:
            qs = qs.filter(target_id=target_id)

        return qs   # pagination (PAGE_SIZE=20) naturally caps output


# ─── User ViewSet ──────────────────────────────────────────────────────────────

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only user list (for auto-completing assignee fields, etc.)

    list     GET /api/users/
    retrieve GET /api/users/{id}/
    me       GET /api/users/me/
    """
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['username', 'email', 'first_name', 'last_name']
    ordering_fields    = ['username', 'date_joined']
    ordering           = ['username']

    def get_queryset(self):
        return User.objects.filter(is_active=True)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """GET /api/users/me/ — returns the currently authenticated user."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
