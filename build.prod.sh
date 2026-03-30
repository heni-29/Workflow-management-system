#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input

# Optional: create admin user during deploy when shell access is unavailable.
if [ "${CREATE_SUPERUSER_ON_DEPLOY:-0}" = "1" ]; then
	python manage.py create_superuser
fi
