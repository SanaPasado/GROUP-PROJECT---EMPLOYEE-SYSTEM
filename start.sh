#!/usr/bin/env bash
# exit on error
set -o errexit

# Run database migrations
python manage.py migrate

# Start the application
gunicorn Employee_System.wsgi:application --bind 0.0.0.0:$PORT
