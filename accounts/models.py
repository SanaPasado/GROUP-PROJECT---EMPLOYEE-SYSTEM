from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from Employee_System import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField


def gmail_only_validator(value):
    if not value.lower().endswith('@gmail.com'):
        raise ValidationError('Email must end with @gmail.com')

def image_file_validator(value):
    """Validate image file extensions for Cloudinary uploads"""
    if hasattr(value, 'name') and value.name:
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        file_extension = value.name.lower().split('.')[-1]
        if file_extension not in allowed_extensions:
            raise ValidationError(
                f'Only {", ".join(allowed_extensions).upper()} files are allowed. '
                f'You uploaded a {file_extension.upper()} file.'
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
    phone_number = PhoneNumberField(region='PH', help_text='Enter a Philippine phone number')
    date_hired = models.DateField(default=timezone.now)
    emergency_contact = PhoneNumberField(region='PH', help_text='Enter a Philippine phone number for emergency contact')
    photo = CloudinaryField('image', default='blank-profile-picture', validators=[image_file_validator])
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

    def send_paycheck_notification(self, amount=None, message="Your paycheck has been sent!", notification_type="paycheck", sent_by=None):
        """Send a paycheck notification to this employee"""
        from notifications.models import PaycheckNotification

        notification = PaycheckNotification.objects.create(
            employee=self,
            notification_type=notification_type,
            message=message,
            amount=amount,
            sent_by=sent_by
        )
        return notification

    def get_paycheck_notifications(self, limit=20):
        """Get paycheck notifications for this employee"""
        from notifications.models import PaycheckNotification
        return PaycheckNotification.objects.filter(
            employee=self
        ).order_by('-sent_at')[:limit]

    def get_unread_notifications_count(self):
        """Get count of unread paycheck notifications"""
        from notifications.models import PaycheckNotification
        return PaycheckNotification.objects.filter(
            employee=self,
            is_read=False
        ).count()

    def mark_all_notifications_read(self):
        """Mark all paycheck notifications as read for this employee"""
        from notifications.models import PaycheckNotification
        return PaycheckNotification.objects.filter(
            employee=self,
            is_read=False
        ).update(is_read=True)

    @classmethod
    def send_bulk_paycheck_notifications(cls, employee_ids, amount=None, message="Your paycheck has been sent!", notification_type="paycheck", sent_by=None):
        """Class method to send paycheck notifications to multiple employees"""
        from notifications.models import PaycheckNotification

        employees = cls.objects.filter(id__in=employee_ids, active=True)
        notifications = []

        for employee in employees:
            notifications.append(PaycheckNotification(
                employee=employee,
                notification_type=notification_type,
                message=message,
                amount=amount,
                sent_by=sent_by
            ))

        PaycheckNotification.objects.bulk_create(notifications)
        return len(notifications)
