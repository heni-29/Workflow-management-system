# api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from projects.models import Project
from tasks.models import Task, TaskStatus, TaskPriority
from activities.models import ActivityLog

User = get_user_model()


# ─── User ──────────────────────────────────────────────────────────────────────

class UserMinimalSerializer(serializers.ModelSerializer):
    """Compact user representation used as a nested field."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """Full public user profile (no password)."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'is_active']
        read_only_fields = ['date_joined', 'is_active']


# ─── Project ───────────────────────────────────────────────────────────────────

class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserMinimalSerializer(read_only=True)
    members    = UserMinimalSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True,
        source='members', required=False
    )
    task_count        = serializers.SerializerMethodField()
    open_task_count   = serializers.SerializerMethodField()

    class Meta:
        model  = Project
        fields = [
            'id', 'name', 'description',
            'created_by', 'members', 'member_ids',
            'task_count', 'open_task_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_task_count(self, obj):
        return obj.tasks.count()

    def get_open_task_count(self, obj):
        return obj.tasks.exclude(status=TaskStatus.DONE).count()

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        project = Project.objects.create(**validated_data)
        project.members.set(members)
        return project

    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance


# ─── Task ──────────────────────────────────────────────────────────────────────

class TaskSerializer(serializers.ModelSerializer):
    assignee = UserMinimalSerializer(read_only=True)
    reporter = UserMinimalSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True,
        source='assignee', required=False, allow_null=True
    )
    project_name     = serializers.CharField(source='project.name', read_only=True)
    status_display   = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue       = serializers.SerializerMethodField()

    class Meta:
        model  = Task
        fields = [
            'id', 'title', 'description',
            'project', 'project_name',
            'assignee', 'assignee_id',
            'reporter',
            'status', 'status_display',
            'priority', 'priority_display',
            'due_date', 'is_overdue',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'reporter', 'created_at', 'updated_at']

    def get_is_overdue(self, obj):
        from django.utils import timezone
        if obj.due_date and obj.status != TaskStatus.DONE:
            return obj.due_date < timezone.now().date()
        return False

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['reporter'] = request.user if request else None
        return super().create(validated_data)


class TaskStatusUpdateSerializer(serializers.Serializer):
    """Lightweight serializer just for PATCH /tasks/{id}/set_status/"""
    status = serializers.ChoiceField(choices=TaskStatus.choices)


# ─── Activity ──────────────────────────────────────────────────────────────────

class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model  = ActivityLog
        fields = ['id', 'user', 'verb', 'target_type', 'target_id', 'detail', 'timestamp']
        read_only_fields = fields
