import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    """A custom management command to create a superuser non-interactively."""
    help = 'Creates a superuser from environment variables.'

    def handle(self, *args, **options):
        User = get_user_model()
        email = os.environ.get('SUPERUSER_EMAIL')
        password = os.environ.get('SUPERUSER_PASSWORD')
        first_name = os.environ.get('SUPERUSER_FIRST_NAME')
        last_name = os.environ.get('SUPERUSER_LAST_NAME')

        if not all([email, password, first_name, last_name]):
            self.stdout.write(self.style.ERROR('Missing SUPERUSER_EMAIL, SUPERUSER_PASSWORD, SUPERUSER_FIRST_NAME, or SUPERUSER_LAST_NAME environment variables.'))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Superuser with email "{email}" already exists. Skipping.'))
        else:
            # Create the superuser with the fields required by the custom Employee model
            User.objects.create_superuser(email=email, password=password, first_name=first_name, last_name=last_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser with email "{email}"'))
