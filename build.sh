#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py createsuperuser \
  --noinput \

  --email $DJANGO_SUPERUSER_EMAIL || true
