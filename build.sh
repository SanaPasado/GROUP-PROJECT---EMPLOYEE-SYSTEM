#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# DEBUGGING: List the contents of the staticfiles directory
echo "--- Contents of staticfiles directory ---"
ls -R staticfiles
echo "-------------------------------------"

# Run database migrations
python manage.py migrate
