import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    """A custom management command to create a superuser non-interactively."""
    help = 'Creates a superuser from environment variables.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('SUPERUSER_USERNAME')
        email = os.environ.get('SUPERUSER_EMAIL')
        password = os.environ.get('SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.ERROR('Missing SUPERUSER_USERNAME, SUPERUSER_EMAIL, or SUPERUSER_PASSWORD environment variables.'))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Superuser with email "{email}" already exists. Skipping.'))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{username}"'))
