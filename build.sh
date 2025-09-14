#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py createsuperuser \
  --noinput \
  --username $DJANGO_SUPERUSER_USERNAME \
  --email $DJANGO_SUPERUSER_EMAIL || true

python manage.py shell -c "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
u, created = User.objects.get_or_create(username='$DJANGO_SUPERUSER_USERNAME'); \
u.first_name='$DJANGO_SUPERUSER_FIRSTNAME'; \
u.last_name='$DJANGO_SUPERUSER_LASTNAME'; \
u.set_password('$DJANGO_SUPERUSER_PASSWORD'); \
u.save()"