#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('djangoadmin', 'admin@example.com', '12admin34') if not User.objects.filter(username='djangoadmin').exists() else print('Superuser already exists')"
