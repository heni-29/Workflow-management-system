from django.test import TestCase
from django.contrib.auth import get_user_model
from projects.models import Project
from tasks.models import Task

User = get_user_model()

class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='p')
        self.project = Project.objects.create(name='P', created_by=self.user)

    def test_create_task(self):
        task = Task.objects.create(title='T', project=self.project, reporter=self.user)
        self.assertEqual(task.status, 'todo')
        self.assertIn(task, self.project.tasks.all())
