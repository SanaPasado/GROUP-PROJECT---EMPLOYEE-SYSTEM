from cloudinary.models import CloudinaryField
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from cloudinary.models import CloudinaryField
from Employee_System import settings
import re
from django.core.exceptions import ValidationError


def gmail_only_validator(value):
    if not value.lower().endswith('@gmail.com'):
        raise ValidationError('Email must end with @gmail.com')

def philippine_phone_validator(value):
    # Remove any spaces, dashes, or parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', value)

    # Check for valid Philippine phone number formats
    # +63XXXXXXXXXX (country code format)
    # 09XXXXXXXXX (mobile format)
    # 02XXXXXXX or 032XXXXXXX etc. (landline format)

    patterns = [
        r'^\+639\d{9}$',  # +639XXXXXXXXX (mobile with country code)
        r'^09\d{9}$',     # 09XXXXXXXXX (mobile)
        r'^0\d{1,2}\d{7,8}$'  # landline formats (02XXXXXXX, 032XXXXXXXX, etc.)
    ]

    if not any(re.match(pattern, cleaned) for pattern in patterns):
        raise ValidationError(
            'Enter a valid Philippine phone number (e.g., +639XXXXXXXXX, 09XXXXXXXXX, or landline)'
        )


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_active=True, is_staff=False, is_admin=False, is_superuser=False, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')

        user_obj = self.model(
            email=self.normalize_email(email),
            **extra_fields  # This is the line that handles first_name and last_name
        )
        user_obj.set_password(password)
        user_obj.active = is_active
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_superuser = is_superuser # Correctly handle the is_superuser field
        user_obj.save(using=self._db)

        return user_obj

    def create_staffuser(self, email, password=None, **extra_fields):
        user = self.create_user(
            email,
            password=password,
            is_active=True,
            is_staff=True,
            **extra_fields
        )
        return user


    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(
            email,
            password=password,
            is_active=True,
            is_staff=True,
            is_admin=True,
            is_superuser=True, # Ensure superusers are created with is_superuser=True
            **extra_fields
        )
        return user



class Employee(AbstractBaseUser, PermissionsMixin):
    #user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True, validators=[gmail_only_validator])
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    salary = models.FloatField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, validators=[philippine_phone_validator])
    date_hired = models.DateField(default=timezone.now)
    emergency_contact = models.CharField(max_length=20, validators=[philippine_phone_validator])
    photo = CloudinaryField('image', default='blank-profile-picture')
        # validators = [FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])])
    address = models.CharField(max_length=255, null=True, blank=True)
    vacation_days = models.IntegerField(null=True, blank=True)
    work_schedule = models.CharField(null=True, blank=True)
    sick_leaves = models.IntegerField(null=True, blank=True)
    is_online = models.BooleanField(default= False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    totp_secret = models.CharField(max_length=32, blank=True, null=True, help_text="TOTP secret for Google Authenticator")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    objects = UserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.first_name}-{self.last_name}")
            slug = base_slug
            num = 1
            while Employee.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active
