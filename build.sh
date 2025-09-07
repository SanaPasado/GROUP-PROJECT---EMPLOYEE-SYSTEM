#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Create superuser if it doesn't exist (optional)
# python manage.py shell -c "from accounts.models import Employee; Employee.objects.filter(email='admin@example.com').exists() or Employee.objects.create_superuser('admin@example.com', 'admin123', first_name='Admin', last_name='User')"
