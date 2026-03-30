#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input

is_enabled() {
	case "${1:-0}" in
		1|true|TRUE|yes|YES|on|ON) return 0 ;;
		*) return 1 ;;
	esac
}

# Optional: create admin user during deploy when shell access is unavailable.
if is_enabled "${CREATE_SUPERUSER_ON_DEPLOY:-0}"; then
	echo "[deploy] CREATE_SUPERUSER_ON_DEPLOY enabled"
	python manage.py create_superuser
else
	echo "[deploy] CREATE_SUPERUSER_ON_DEPLOY disabled"
fi

# Optional: seed demo data (destructive). Use once, then reset to 0.
if is_enabled "${POPULATE_DEMO_DATA_ON_DEPLOY:-0}"; then
	echo "[deploy] POPULATE_DEMO_DATA_ON_DEPLOY enabled"
	python manage.py populate_data
else
	echo "[deploy] POPULATE_DEMO_DATA_ON_DEPLOY disabled"
fi
