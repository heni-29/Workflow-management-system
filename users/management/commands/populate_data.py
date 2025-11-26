from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Project
from tasks.models import Task, TaskStatus, TaskPriority
from activities.models import ActivityLog

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        # Get or create admin user
        admin = User.objects.filter(username='djangoadmin').first()
        if not admin:
            self.stdout.write(self.style.ERROR('Admin user not found. Please create superuser first.'))
            return

        # Create sample projects
        projects_data = [
            {
                'name': 'E-Commerce Platform',
                'description': 'Building a modern e-commerce platform with React and Django. Features include product catalog, shopping cart, payment integration, and order management.',
            },
            {
                'name': 'Mobile App Development',
                'description': 'Cross-platform mobile application using React Native. Includes user authentication, real-time notifications, and offline support.',
            },
            {
                'name': 'Data Analytics Dashboard',
                'description': 'Interactive dashboard for visualizing business metrics and KPIs. Built with D3.js and Python for data processing.',
            },
        ]

        for proj_data in projects_data:
            project, created = Project.objects.get_or_create(
                name=proj_data['name'],
                defaults={
                    'description': proj_data['description'],
                    'created_by': admin,
                }
            )
            if created:
                project.members.add(admin)
                self.stdout.write(self.style.SUCCESS(f'Created project: {project.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Project already exists: {project.name}'))

        # Create sample tasks
        ecommerce = Project.objects.filter(name='E-Commerce Platform').first()
        mobile = Project.objects.filter(name='Mobile App Development').first()
        analytics = Project.objects.filter(name='Data Analytics Dashboard').first()

        if ecommerce:
            tasks_data = [
                {'title': 'Design product catalog UI', 'status': TaskStatus.DONE, 'priority': TaskPriority.HIGH},
                {'title': 'Implement shopping cart', 'status': TaskStatus.IN_PROGRESS, 'priority': TaskPriority.HIGH},
                {'title': 'Integrate payment gateway', 'status': TaskStatus.TODO, 'priority': TaskPriority.MEDIUM},
                {'title': 'Setup email notifications', 'status': TaskStatus.TODO, 'priority': TaskPriority.LOW},
            ]
            for task_data in tasks_data:
                Task.objects.get_or_create(
                    title=task_data['title'],
                    project=ecommerce,
                    defaults={
                        'status': task_data['status'],
                        'priority': task_data['priority'],
                        'assignee': admin,
                        'reporter': admin,
                    }
                )

        if mobile:
            tasks_data = [
                {'title': 'Setup React Native project', 'status': TaskStatus.DONE, 'priority': TaskPriority.HIGH},
                {'title': 'Implement user authentication', 'status': TaskStatus.REVIEW, 'priority': TaskPriority.HIGH},
                {'title': 'Add push notifications', 'status': TaskStatus.IN_PROGRESS, 'priority': TaskPriority.MEDIUM},
                {'title': 'Create offline mode', 'status': TaskStatus.TODO, 'priority': TaskPriority.MEDIUM},
            ]
            for task_data in tasks_data:
                Task.objects.get_or_create(
                    title=task_data['title'],
                    project=mobile,
                    defaults={
                        'status': task_data['status'],
                        'priority': task_data['priority'],
                        'assignee': admin,
                        'reporter': admin,
                    }
                )

        if analytics:
            tasks_data = [
                {'title': 'Design dashboard layout', 'status': TaskStatus.DONE, 'priority': TaskPriority.HIGH},
                {'title': 'Create data visualization charts', 'status': TaskStatus.IN_PROGRESS, 'priority': TaskPriority.HIGH},
                {'title': 'Implement filters and search', 'status': TaskStatus.TODO, 'priority': TaskPriority.MEDIUM},
                {'title': 'Add export functionality', 'status': TaskStatus.TODO, 'priority': TaskPriority.LOW},
            ]
            for task_data in tasks_data:
                Task.objects.get_or_create(
                    title=task_data['title'],
                    project=analytics,
                    defaults={
                        'status': task_data['status'],
                        'priority': task_data['priority'],
                        'assignee': admin,
                        'reporter': admin,
                    }
                )

        # Create sample activity logs
        ActivityLog.objects.get_or_create(
            user=admin,
            verb='created',
            target_type='project',
            defaults={'detail': {'name': 'E-Commerce Platform'}}
        )
        ActivityLog.objects.get_or_create(
            user=admin,
            verb='updated',
            target_type='task',
            defaults={'detail': {'task': 'Implement shopping cart', 'status': 'In Progress'}}
        )

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
