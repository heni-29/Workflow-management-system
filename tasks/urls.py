# tasks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('kanban/', views.kanban_board, name='kanban_board'),
    path('kanban/<int:project_id>/', views.kanban_board, name='kanban_board_project'),
    path('<int:task_id>/update-status/', views.task_update_status, name='task_update_status'),
]
