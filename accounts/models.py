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


def employee_photo_upload_path(instance, filename):
    """Generate upload path for employee photos"""
    return f'employee-photos/{instance.slug}_{filename}'


def get_current_date():
    """Return current date for default value"""
    return timezone.now().date()


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

    # Simplified Salary Fields
    salary = models.FloatField(null=True, blank=True, help_text='Annual salary')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Regular hourly wage rate')
    overtime_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Overtime hourly rate (auto-calculated as hourly_rate + 0.5)')

    phone_number = PhoneNumberField(region='PH', help_text='Enter a Philippine phone number')
    date_hired = models.DateField(default=get_current_date)
    emergency_contact = PhoneNumberField(region='PH', help_text='Enter a Philippine phone number for emergency contact')
    photo = CloudinaryField('image',
                           default='blank-profile-picture',
                           null=True,
                           blank=True,
                           transformation={
                               'width': 300,
                               'height': 300,
                               'crop': 'fill',
                               'gravity': 'face',
                               'quality': 'auto',
                               'format': 'auto'
                           },
                           help_text='Upload employee photo (JPG, PNG, GIF, WEBP formats supported)')
    # photo = models.ImageField(upload_to=employee_photo_upload_path, null=True, blank=True, validators=[image_file_validator])
    address = models.CharField(max_length=255, null=True, blank=True)
    vacation_days = models.IntegerField(null=True, blank=True)
    sick_leaves = models.IntegerField(null=True, blank=True)

    # Enhanced Working Hours Fields
    work_start_time = models.TimeField(default='08:00', help_text='Standard work start time')
    work_end_time = models.TimeField(default='17:00', help_text='Standard work end time')
    weekly_hours = models.DecimalField(max_digits=5, decimal_places=2, default=40.00, help_text='Expected weekly work hours')

    # Online Status (based on attendance)
    is_online = models.BooleanField(default=False)
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

        # Auto-calculate hourly rate from salary if not provided
        if self.salary and not self.hourly_rate:
            # Assuming 52 weeks per year
            self.hourly_rate = round(self.salary / (52 * float(self.weekly_hours)), 2)
        # Auto-calculate salary from hourly rate if not provided
        elif self.hourly_rate and not self.salary:
            self.salary = float(self.hourly_rate) * float(self.weekly_hours) * 52

        # Auto-calculate overtime rate (hourly rate + 0.5)
        if self.hourly_rate:
            self.overtime_rate = float(self.hourly_rate) + 0.5

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

    def get_full_name(self):
        """Return full name of employee"""
        return f"{self.first_name} {self.last_name}"

    def get_working_hours_display(self):
        """Return formatted working hours"""
        return f"{self.work_start_time.strftime('%H:%M')} - {self.work_end_time.strftime('%H:%M')}"

    def is_currently_working(self):
        """Check if employee is currently at work based on today's attendance"""
        try:
            from attendance.models import Attendance
            today_attendance = Attendance.objects.get(employee=self, date=timezone.now().date())
            return today_attendance.time_in is not None and today_attendance.time_out is None
        except:
            return False

    def get_current_work_duration(self):
        """Get current work session duration if employee is currently working"""
        if self.is_currently_working():
            try:
                from attendance.models import Attendance
                today_attendance = Attendance.objects.get(employee=self, date=timezone.now().date())
                if today_attendance.time_in:
                    duration = timezone.now() - today_attendance.time_in
                    total_minutes = int(duration.total_seconds() / 60)
                    hours = total_minutes // 60
                    minutes = total_minutes % 60
                    return f"{hours}h {minutes}m"
            except:
                pass
        return "Not working"

    def calculate_payroll_breakdown(self, start_date=None, end_date=None):
        """Calculate detailed payroll breakdown including approved overtime"""
        from attendance.models import Attendance
        from datetime import datetime, timedelta

        # Default to current week if no dates provided
        if not start_date or not end_date:
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())  # Monday
            end_date = start_date + timedelta(days=6)  # Sunday

        # Get all attendance records for the period
        attendance_records = Attendance.objects.filter(
            employee=self,
            date__range=[start_date, end_date],
            time_in__isnull=False,
            time_out__isnull=False
        )

        regular_hours = 0
        approved_overtime_hours = 0
        total_overtime_hours = 0  # For tracking purposes

        for record in attendance_records:
            # Calculate daily hours worked
            duration = record.time_out - record.time_in
            daily_hours = duration.total_seconds() / 3600

            # Expected daily hours (weekly_hours / 5 days)
            expected_daily_hours = float(self.weekly_hours) / 5

            if daily_hours <= expected_daily_hours:
                # All hours are regular
                regular_hours += daily_hours
            else:
                # Split into regular and overtime
                regular_hours += expected_daily_hours
                overtime_for_day = daily_hours - expected_daily_hours
                total_overtime_hours += overtime_for_day

                # Only count overtime if approved
                if record.overtime_approved:
                    approved_overtime_hours += overtime_for_day

        # Calculate pay amounts
        regular_pay = regular_hours * float(self.hourly_rate) if self.hourly_rate else 0
        overtime_pay = approved_overtime_hours * float(self.overtime_rate) if self.overtime_rate else 0
        total_pay = regular_pay + overtime_pay

        return {
            'period_start': start_date,
            'period_end': end_date,
            'regular_hours': round(regular_hours, 2),
            'approved_overtime_hours': round(approved_overtime_hours, 2),
            'total_overtime_hours': round(total_overtime_hours, 2),  # For admin reference
            'unapproved_overtime_hours': round(total_overtime_hours - approved_overtime_hours, 2),
            'regular_pay': round(regular_pay, 2),
            'overtime_pay': round(overtime_pay, 2),
            'total_pay': round(total_pay, 2),
            'hourly_rate': float(self.hourly_rate) if self.hourly_rate else 0,
            'overtime_rate': float(self.overtime_rate) if self.overtime_rate else 0,
        }

    def get_suggested_paycheck_amount(self, start_date=None, end_date=None):
        """Get suggested paycheck amount based on approved hours only"""
        breakdown = self.calculate_payroll_breakdown(start_date, end_date)
        return breakdown['total_pay']

    def get_pending_overtime_hours(self, start_date=None, end_date=None):
        """Get overtime hours pending approval"""
        from attendance.models import Attendance
        from datetime import datetime, timedelta

        if not start_date or not end_date:
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)

        pending_records = Attendance.objects.filter(
            employee=self,
            date__range=[start_date, end_date],
            overtime_hours__gt=0,
            overtime_approved=False,
            overtime_rejected=False
        )

        return sum(record.overtime_hours for record in pending_records)

    def has_paycheck_sent_for_period(self, start_date, end_date):
        """Check if paycheck has already been sent for this period"""
        from notifications.models import PaycheckNotification

        return PaycheckNotification.objects.filter(
            employee=self,
            sent_at__date__range=[start_date, end_date]
        ).exists()
