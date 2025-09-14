"""
WSGI config for Employee_System project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Employee_System.settings')

# Get the standard Django application
application = get_wsgi_application()

# Wrap the application with WhiteNoise to serve static files.
# The line for serving media files has been removed to allow Cloudinary to handle it.
if not settings.DEBUG:
    application = WhiteNoise(application, root=settings.STATIC_ROOT)
