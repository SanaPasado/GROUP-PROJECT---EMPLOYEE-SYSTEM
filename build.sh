#!/usr/bin/env bash
# exit on error
set -o errexit

# Diagnostic commands to check Cloudinary environment variables
echo "--- Checking Cloudinary Vars ---"
echo "Cloud Name Is: $CLOUDINARY_CLOUD_NAME"
echo "API Key Is: $CLOUDINARY_API_KEY"
echo "API Secret Is: $CLOUDINARY_API_SECRET"
echo "--- End Check ---"

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser if it doesn't exist
#python manage.py createsuperuser \
#  --noinput \
#
#  --email $DJANGO_SUPERUSER_EMAIL || true
