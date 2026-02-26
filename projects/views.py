# projects/views.py
import datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from .models import Project
from tasks.models import Task, TaskStatus


@login_required
def home(request):
    projects = Project.objects.prefetch_related('members').all()[:50]
    return render(request, 'projects/home.html', {'projects': projects})


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.prefetch_related('members').select_related('created_by'),
        pk=project_id,
    )
    tasks_qs = Task.objects.filter(project=project).select_related('assignee', 'reporter')

    today = datetime.date.today()

    # ── Per-status counts ──────────────────────────────────────────────
    status_counts = {
        'todo':        tasks_qs.filter(status=TaskStatus.TODO).count(),
        'in_progress': tasks_qs.filter(status=TaskStatus.IN_PROGRESS).count(),
        'review':      tasks_qs.filter(status=TaskStatus.REVIEW).count(),
        'done':        tasks_qs.filter(status=TaskStatus.DONE).count(),
    }
    total_tasks  = sum(status_counts.values())
    done_pct     = round(status_counts['done'] / total_tasks * 100) if total_tasks else 0
    overdue      = tasks_qs.filter(due_date__lt=today).exclude(status=TaskStatus.DONE).count()

    # ── Members enriched with their assigned task count ───────────────
    members = []
    for m in project.members.all():
        assigned = tasks_qs.filter(assignee=m).count()
        done_cnt = tasks_qs.filter(assignee=m, status=TaskStatus.DONE).count()
        members.append({'user': m, 'assigned': assigned, 'done': done_cnt})

    # ── Recent tasks (latest 6) ────────────────────────────────────────
    recent_tasks = tasks_qs.order_by('-updated_at')[:6]

    return render(request, 'projects/detail.html', {
        'project':       project,
        'status_counts': status_counts,
        'total_tasks':   total_tasks,
        'done_pct':      done_pct,
        'overdue':       overdue,
        'members':       members,
        'recent_tasks':  recent_tasks,
        'today':         today,
    })

# dashboard view (Plotly)
from tasks.models import Task
from django.db.models import Count
import plotly.graph_objects as go
import plotly.io as pio

@login_required
def project_dashboard(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    tasks = Task.objects.filter(project=project)

    status_counts = list(tasks.values('status').annotate(count=Count('status')))
    labels = [s['status'] for s in status_counts]
    values = [s['count'] for s in status_counts]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
    fig.update_layout(title_text='Task status distribution')

    graph_html = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)

    return render(request, 'projects/dashboard.html', {
        'project': project,
        'graph_html': graph_html,
    })
