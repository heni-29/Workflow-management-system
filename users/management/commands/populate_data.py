from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from projects.models import Project
from tasks.models import Task, TaskStatus, TaskPriority
from activities.models import ActivityLog

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with rich sample data (projects + tasks + activities)'

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def _due(self, offset_days):
        """Return a date relative to today."""
        return date.today() + timedelta(days=offset_days)

    def handle(self, *args, **options):
        # ── Admin user ────────────────────────────────────────────────
        admin = User.objects.filter(username='djangoadmin').first()
        if not admin:
            self.stdout.write(self.style.ERROR(
                'Admin user "djangoadmin" not found. Create a superuser first.'
            ))
            return

        # ── Extra team members ─────────────────────────────────────────
        members_info = [
            ('alice',   'Alice',   'Johnson', 'alice@workflow.dev'),
            ('bob',     'Bob',     'Smith',   'bob@workflow.dev'),
            ('carol',   'Carol',   'Lee',     'carol@workflow.dev'),
            ('david',   'David',   'Kim',     'david@workflow.dev'),
        ]
        team = {'admin': admin}
        for username, first, last, email in members_info:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': first, 'last_name': last, 'email': email},
            )
            if created:
                user.set_password('pass1234')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  Created user: {username}'))
            team[username] = user

        # ── Projects ──────────────────────────────────────────────────
        projects_data = [
            {
                'name': 'E-Commerce Platform',
                'description': (
                    'Building a modern e-commerce platform with React and Django. '
                    'Features include product catalog, shopping cart, payment integration, '
                    'and order management.'
                ),
                'members': ['admin', 'alice', 'bob'],
            },
            {
                'name': 'Mobile App Development',
                'description': (
                    'Cross-platform mobile application using React Native. '
                    'Includes user authentication, real-time notifications, and offline support.'
                ),
                'members': ['admin', 'carol', 'david'],
            },
            {
                'name': 'Data Analytics Dashboard',
                'description': (
                    'Interactive dashboard for visualising business metrics and KPIs. '
                    'Built with D3.js and Python for data processing.'
                ),
                'members': ['admin', 'alice', 'david'],
            },
            {
                'name': 'DevOps & CI/CD Pipeline',
                'description': (
                    'Automating build, test, and deployment workflows using GitHub Actions, '
                    'Docker, and Kubernetes. Targets zero-downtime blue/green deployments.'
                ),
                'members': ['admin', 'bob'],
            },
            {
                'name': 'AI Chatbot Integration',
                'description': (
                    'Embedding an LLM-powered assistant into the customer support portal. '
                    'Uses OpenAI API, LangChain, and a vector database for context retrieval.'
                ),
                'members': ['admin', 'alice', 'carol'],
            },
            {
                'name': 'Internal HR Portal',
                'description': (
                    'Self-service HR portal for leave requests, payroll slips, performance '
                    'reviews, and onboarding checklists. Built with Django + HTMX.'
                ),
                'members': ['admin', 'carol'],
            },
            {
                'name': 'Security Audit & Hardening',
                'description': (
                    'Company-wide security review: penetration testing, dependency scanning, '
                    'secrets rotation, and implementing an OWASP-compliant checklist.'
                ),
                'members': ['admin', 'david', 'bob'],
            },
            {
                'name': 'Marketing Website Redesign',
                'description': (
                    'Full redesign of the public marketing site using Next.js and a headless '
                    'CMS. Goal: improve Core Web Vitals scores and lead conversion by 30 %.'
                ),
                'members': ['admin', 'alice'],
            },
        ]

        project_objs = {}
        for pd in projects_data:
            proj, created = Project.objects.get_or_create(
                name=pd['name'],
                defaults={'description': pd['description'], 'created_by': admin},
            )
            for m in pd['members']:
                proj.members.add(team[m])
            verb = 'Created' if created else 'Already exists'
            style = self.style.SUCCESS if created else self.style.WARNING
            self.stdout.write(style(f'  {verb} project: {proj.name}'))
            project_objs[pd['name']] = proj

        # ── Tasks ──────────────────────────────────────────────────────
        # Format: (title, status, priority, assignee_key, due_offset_days)
        tasks_map = {
            'E-Commerce Platform': [
                ('Design product catalog UI',       TaskStatus.DONE,        TaskPriority.HIGH,   'alice',  -20),
                ('Implement shopping cart',         TaskStatus.IN_PROGRESS, TaskPriority.HIGH,   'bob',     10),
                ('Integrate Stripe payment gateway',TaskStatus.REVIEW,      TaskPriority.HIGH,   'admin',    5),
                ('Add product search & filters',    TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 'alice',   14),
                ('Setup email order notifications', TaskStatus.TODO,        TaskPriority.MEDIUM, 'bob',     21),
                ('Write unit tests for cart logic', TaskStatus.TODO,        TaskPriority.MEDIUM, 'alice',   18),
                ('Performance optimise image CDN',  TaskStatus.TODO,        TaskPriority.LOW,    'bob',     30),
                ('Accessibility audit (WCAG 2.1)',  TaskStatus.DONE,        TaskPriority.MEDIUM, 'admin',  -10),
            ],
            'Mobile App Development': [
                ('Setup React Native project',      TaskStatus.DONE,        TaskPriority.HIGH,   'carol',  -30),
                ('Implement user authentication',   TaskStatus.DONE,        TaskPriority.HIGH,   'david',  -15),
                ('Add push notifications',          TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 'carol',    8),
                ('Build offline sync layer',        TaskStatus.TODO,        TaskPriority.MEDIUM, 'david',   20),
                ('Create onboarding screens',       TaskStatus.REVIEW,      TaskPriority.LOW,    'carol',    3),
                ('Integrate Google Maps SDK',       TaskStatus.IN_PROGRESS, TaskPriority.HIGH,   'david',   12),
                ('Submit to App Store & Play Store',TaskStatus.TODO,        TaskPriority.HIGH,   'admin',   45),
            ],
            'Data Analytics Dashboard': [
                ('Design dashboard wireframes',     TaskStatus.DONE,        TaskPriority.HIGH,   'alice',  -25),
                ('Build D3.js bar & line charts',   TaskStatus.DONE,        TaskPriority.HIGH,   'david',  -10),
                ('Implement date-range filters',    TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 'alice',    7),
                ('Add CSV/Excel export',            TaskStatus.TODO,        TaskPriority.MEDIUM, 'david',   15),
                ('Create user role permissions',    TaskStatus.REVIEW,      TaskPriority.HIGH,   'admin',    2),
                ('Write API integration tests',     TaskStatus.TODO,        TaskPriority.LOW,    'alice',   25),
                ('Dark mode theme support',         TaskStatus.TODO,        TaskPriority.LOW,    'david',   35),
            ],
            'DevOps & CI/CD Pipeline': [
                ('Dockerise all microservices',     TaskStatus.DONE,        TaskPriority.HIGH,   'bob',    -20),
                ('Setup GitHub Actions workflows',  TaskStatus.DONE,        TaskPriority.HIGH,   'admin',  -12),
                ('Configure Kubernetes cluster',    TaskStatus.IN_PROGRESS, TaskPriority.HIGH,   'bob',      9),
                ('Implement blue/green deployment', TaskStatus.TODO,        TaskPriority.HIGH,   'admin',   16),
                ('Add Prometheus + Grafana alerts', TaskStatus.TODO,        TaskPriority.MEDIUM, 'bob',     22),
                ('Document runbook & playbooks',    TaskStatus.TODO,        TaskPriority.LOW,    'admin',   30),
            ],
            'AI Chatbot Integration': [
                ('Define chatbot scope & personas', TaskStatus.DONE,        TaskPriority.HIGH,   'alice',  -18),
                ('Setup OpenAI API integration',    TaskStatus.DONE,        TaskPriority.HIGH,   'admin',   -8),
                ('Build vector store with Pinecone',TaskStatus.IN_PROGRESS, TaskPriority.HIGH,   'alice',    6),
                ('Design conversation UI widget',   TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 'carol',   11),
                ('Implement fallback to human agent',TaskStatus.REVIEW,     TaskPriority.MEDIUM, 'admin',    4),
                ('A/B test chatbot vs no chatbot',  TaskStatus.TODO,        TaskPriority.LOW,    'carol',   28),
                ('GDPR data retention policy',      TaskStatus.TODO,        TaskPriority.HIGH,   'alice',   20),
            ],
            'Internal HR Portal': [
                ('Gather requirements from HR team',TaskStatus.DONE,        TaskPriority.HIGH,   'carol',  -22),
                ('Design leave request workflow',   TaskStatus.DONE,        TaskPriority.HIGH,   'carol',  -10),
                ('Implement payroll slip viewer',   TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 'carol',    7),
                ('Build performance review module', TaskStatus.TODO,        TaskPriority.MEDIUM, 'admin',   18),
                ('Onboarding checklist feature',    TaskStatus.TODO,        TaskPriority.LOW,    'carol',   30),
                ('SSO integration (Google OAuth)',  TaskStatus.REVIEW,      TaskPriority.HIGH,   'admin',    1),
            ],
            'Security Audit & Hardening': [
                ('Run OWASP ZAP penetration test',  TaskStatus.DONE,        TaskPriority.HIGH,   'david',  -15),
                ('Rotate all production secrets',   TaskStatus.DONE,        TaskPriority.HIGH,   'bob',     -5),
                ('Enable 2FA for admin accounts',   TaskStatus.DONE,        TaskPriority.HIGH,   'admin',   -3),
                ('Dependency vulnerability scan',   TaskStatus.IN_PROGRESS, TaskPriority.HIGH,   'david',    4),
                ('Implement CSP headers',           TaskStatus.REVIEW,      TaskPriority.MEDIUM, 'bob',      2),
                ('Security training workshop',      TaskStatus.TODO,        TaskPriority.LOW,    'admin',   14),
                ('Third-party vendor risk review',  TaskStatus.TODO,        TaskPriority.MEDIUM, 'david',   20),
            ],
            'Marketing Website Redesign': [
                ('Stakeholder kickoff meeting',     TaskStatus.DONE,        TaskPriority.HIGH,   'alice',  -28),
                ('Create Figma design system',      TaskStatus.DONE,        TaskPriority.HIGH,   'alice',  -14),
                ('Build Next.js project scaffold',  TaskStatus.DONE,        TaskPriority.MEDIUM, 'admin',   -7),
                ('Develop homepage hero section',   TaskStatus.IN_PROGRESS, TaskPriority.HIGH,   'alice',    5),
                ('Implement CMS content models',    TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 'admin',    9),
                ('SEO meta-tag optimisation',       TaskStatus.TODO,        TaskPriority.MEDIUM, 'alice',   15),
                ('Launch staging environment',      TaskStatus.TODO,        TaskPriority.HIGH,   'admin',   20),
                ('UAT sign-off & go-live',          TaskStatus.TODO,        TaskPriority.HIGH,   'alice',   35),
            ],
        }

        total_tasks = 0
        for proj_name, task_list in tasks_map.items():
            proj = project_objs.get(proj_name)
            if not proj:
                continue
            for title, status, priority, assignee_key, due_offset in task_list:
                _, created = Task.objects.get_or_create(
                    title=title,
                    project=proj,
                    defaults={
                        'status':    status,
                        'priority':  priority,
                        'assignee':  team.get(assignee_key, admin),
                        'reporter':  admin,
                        'due_date':  self._due(due_offset),
                    },
                )
                if created:
                    total_tasks += 1

        self.stdout.write(self.style.SUCCESS(f'  Created {total_tasks} new tasks'))

        # ── Activity logs ──────────────────────────────────────────────
        activities = [
            (admin,        'created',  'project', 'Launched E-Commerce Platform project'),
            (team['alice'],'created',  'task',    'Added task: Design product catalog UI'),
            (team['bob'],  'updated',  'task',    'Moved "Implement shopping cart" → In Progress'),
            (team['carol'],'created',  'project', 'Launched Mobile App Development project'),
            (team['david'],'completed','task',    'Marked "Implement user authentication" as Done'),
            (admin,        'created',  'project', 'Kicked off AI Chatbot Integration project'),
            (team['alice'],'updated',  'task',    'Moved "Build vector store" → In Progress'),
            (team['bob'],  'completed','task',    'Rotated all production secrets'),
            (admin,        'updated',  'project', 'Added members to Security Audit project'),
            (team['carol'],'created',  'task',    'Added onboarding checklist feature task'),
        ]
        for user, verb, target_type, detail_text in activities:
            ActivityLog.objects.get_or_create(
                user=user,
                verb=verb,
                target_type=target_type,
                defaults={'detail': {'message': detail_text}},
            )

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data populated successfully!'))
