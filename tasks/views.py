# tasks/views.py
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Task, TaskStatus
from .forms import TaskForm
from projects.models import Project


@login_required
def task_list(request):
    tasks = Task.objects.select_related('project', 'assignee').all()[:200]
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.reporter = request.user
            t.save()
            form.save_m2m()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def kanban_board(request, project_id=None):
    """Kanban board view — scoped to a project or global across all projects."""
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        tasks_qs = Task.objects.filter(project=project).select_related('assignee', 'project')
    else:
        project = None
        tasks_qs = Task.objects.select_related('assignee', 'project').all()

    # Bucket tasks by status — include all Tailwind styling so the template
    # can use col.hdr_bg etc. directly (avoids {% with %} inside {% if %}).
    COLOR_MAP = {
        'gray':   {'hdr_bg': 'bg-gray-100',   'hdr_text': 'text-gray-600',  'badge_bg': 'bg-gray-200',   'badge_text': 'text-gray-700',  'col_border': 'border-gray-200',  'dot_color': '#6b7280'},
        'blue':   {'hdr_bg': 'bg-blue-50',    'hdr_text': 'text-blue-700',  'badge_bg': 'bg-blue-100',   'badge_text': 'text-blue-800',  'col_border': 'border-blue-200',  'dot_color': '#3b82f6'},
        'yellow': {'hdr_bg': 'bg-yellow-50',  'hdr_text': 'text-amber-700', 'badge_bg': 'bg-yellow-100', 'badge_text': 'text-yellow-800','col_border': 'border-yellow-200','dot_color': '#f59e0b'},
        'green':  {'hdr_bg': 'bg-green-50',   'hdr_text': 'text-green-700', 'badge_bg': 'bg-green-100',  'badge_text': 'text-green-800', 'col_border': 'border-green-200', 'dot_color': '#22c55e'},
    }
    columns = []
    for key, label, color in [
        (TaskStatus.TODO,        'To Do',       'gray'),
        (TaskStatus.IN_PROGRESS, 'In Progress', 'blue'),
        (TaskStatus.REVIEW,      'In Review',   'yellow'),
        (TaskStatus.DONE,        'Done',        'green'),
    ]:
        col = {'key': key, 'label': label, 'color': color, 'tasks': []}
        col.update(COLOR_MAP[color])
        columns.append(col)
    status_map = {col['key']: col for col in columns}
    for task in tasks_qs:
        col = status_map.get(task.status)
        if col:
            col['tasks'].append(task)

    all_projects = Project.objects.all()
    return render(request, 'tasks/kanban.html', {
        'project': project,
        'columns': columns,
        'all_projects': all_projects,
    })


@login_required
@require_http_methods(['POST'])
def task_update_status(request, task_id):
    """JSON endpoint: update a task's status via drag-and-drop."""
    try:
        data = json.loads(request.body)
        new_status = data.get('status', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    valid_statuses = [s[0] for s in TaskStatus.choices]
    if new_status not in valid_statuses:
        return JsonResponse({'error': f'Invalid status "{new_status}"'}, status=400)

    task = get_object_or_404(Task, pk=task_id)
    task.status = new_status
    task.save(update_fields=['status', 'updated_at'])
    return JsonResponse({'ok': True, 'task_id': task.id, 'status': task.status})
