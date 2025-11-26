# projects/views.py
from django.shortcuts import render, get_object_or_404
from .models import Project

from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    projects = Project.objects.all()[:50]
    return render(request, 'projects/home.html', {'projects': projects})

def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'projects/detail.html', {'project': project})

# dashboard view (Plotly)
from tasks.models import Task
from django.db.models import Count
import plotly.graph_objects as go
import plotly.io as pio

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
