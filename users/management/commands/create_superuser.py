import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a superuser if it does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        debug = os.getenv('DJANGO_DEBUG', '1') == '1'
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'djangoadmin' if debug else '')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com' if debug else '')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '12admin34' if debug else '')

        if not username or not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    'Skipping superuser creation. Set DJANGO_SUPERUSER_USERNAME, '
                    'DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD.'
                )
            )
            return
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists'))
