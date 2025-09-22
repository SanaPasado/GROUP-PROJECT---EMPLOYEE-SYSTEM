from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from Employee_System import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError


def gmail_only_validator(value):
    if not value.lower().endswith('@gmail.com'):
        raise ValidationError('Email must end with @gmail.com')

def image_file_validator(value):
    """Validate image file extensions"""
    if hasattr(value, 'name') and value.name:
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        file_extension = value.name.lower().split('.')[-1]
        if file_extension not in allowed_extensions:
            raise ValidationError(
                f'Only {", ".join(allowed_extensions).upper()} files are allowed. '
                f'You uploaded a {file_extension.upper()} file.'
            )

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
    photo = models.ImageField(upload_to=employee_photo_upload_path, null=True, blank=True, validators=[image_file_validator])
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

    def get_daily_working_hours(self, date=None):
        """Get total working hours for a specific date based on attendance"""
        if date is None:
            date = timezone.now().date()

        try:
            from attendance.models import Attendance
            attendance = Attendance.objects.get(employee=self, date=date)

            if attendance.time_in and attendance.time_out:
                duration = attendance.time_out - attendance.time_in
                total_minutes = int(duration.total_seconds() / 60)
                hours = total_minutes // 60
                minutes = total_minutes % 60
                return f"{hours}h {minutes}m"
            elif attendance.time_in:
                # Currently working - calculate time since time_in
                duration = timezone.now() - attendance.time_in
                total_minutes = int(duration.total_seconds() / 60)
                hours = total_minutes // 60
                minutes = total_minutes % 60
                return f"{hours}h {minutes}m (ongoing)"
            else:
                return "0h 0m"

        except:
            return "No attendance record"

    def get_weekly_working_hours(self):
        """Get total working hours for current week based on attendance"""
        from datetime import timedelta
        from attendance.models import Attendance

        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())

        attendances = Attendance.objects.filter(
            employee=self,
            date__gte=start_of_week,
            date__lte=today
        )

        total_minutes = 0

        for attendance in attendances:
            if attendance.time_in and attendance.time_out:
                duration = attendance.time_out - attendance.time_in
                total_minutes += int(duration.total_seconds() / 60)
            elif attendance.time_in and attendance.date == today:
                # Currently working today
                duration = timezone.now() - attendance.time_in
                total_minutes += int(duration.total_seconds() / 60)

        hours = total_minutes / 60
        return round(hours, 2)

    def get_overtime_hours(self, date=None):
        """Calculate overtime hours for a specific date"""
        if date is None:
            date = timezone.now().date()

        try:
            from attendance.models import Attendance
            attendance = Attendance.objects.get(employee=self, date=date)

            if attendance.time_in and attendance.time_out:
                duration = attendance.time_out - attendance.time_in
                hours_worked = duration.total_seconds() / 3600

                # Calculate expected daily hours (weekly_hours / 5 for 5-day work week)
                expected_daily_hours = float(self.weekly_hours) / 5
                overtime_hours = max(0, hours_worked - expected_daily_hours)
                return round(overtime_hours, 2)
        except:
            pass
        return 0

    def calculate_payroll_breakdown(self, start_date=None, end_date=None):
        """Calculate detailed payroll breakdown for a date range"""
        from datetime import timedelta
        from attendance.models import Attendance

        if not start_date:
            # Default to current week
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
            end_date = today

        attendances = Attendance.objects.filter(
            employee=self,
            date__gte=start_date,
            date__lte=end_date
        )

        regular_hours = 0
        overtime_hours = 0
        total_days_worked = 0

        expected_daily_hours = float(self.weekly_hours) / 5

        for attendance in attendances:
            if attendance.time_in:
                total_days_worked += 1

                if attendance.time_out:
                    duration = attendance.time_out - attendance.time_in
                    hours_worked = duration.total_seconds() / 3600

                    if hours_worked <= expected_daily_hours:
                        regular_hours += hours_worked
                    else:
                        regular_hours += expected_daily_hours
                        overtime_hours += (hours_worked - expected_daily_hours)
                elif attendance.date == timezone.now().date():
                    # Currently working today
                    duration = timezone.now() - attendance.time_in
                    hours_worked = duration.total_seconds() / 3600

                    if hours_worked <= expected_daily_hours:
                        regular_hours += hours_worked
                    else:
                        regular_hours += expected_daily_hours
                        overtime_hours += (hours_worked - expected_daily_hours)

        # Calculate earnings
        regular_pay = regular_hours * float(self.hourly_rate or 0)
        overtime_pay = overtime_hours * float(self.overtime_rate or 0)
        total_pay = regular_pay + overtime_pay

        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_days_worked': total_days_worked,
            'regular_hours': round(regular_hours, 2),
            'overtime_hours': round(overtime_hours, 2),
            'total_hours': round(regular_hours + overtime_hours, 2),
            'hourly_rate': float(self.hourly_rate or 0),
            'overtime_rate': float(self.overtime_rate or 0),
            'regular_pay': round(regular_pay, 2),
            'overtime_pay': round(overtime_pay, 2),
            'total_pay': round(total_pay, 2),
        }

    def get_suggested_paycheck_amount(self):
        """Get suggested paycheck amount based on current week's work"""
        breakdown = self.calculate_payroll_breakdown()
        return breakdown['total_pay']
