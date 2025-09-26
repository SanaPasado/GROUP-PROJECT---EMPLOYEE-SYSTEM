from django.utils import timezone
from django.db import models


def get_current_date():
    """Return current date in the default timezone"""
    return timezone.now().date()


class Attendance(models.Model):
    employee = models.ForeignKey('accounts.Employee', on_delete=models.CASCADE)
    date = models.DateField(default=get_current_date)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)

    # Overtime approval fields
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Calculated overtime hours for this day")
    overtime_approved = models.BooleanField(default=False, help_text="Whether overtime has been approved by admin")
    overtime_rejected = models.BooleanField(default=False, help_text="Whether overtime has been rejected by admin")
    overtime_approved_by = models.ForeignKey('accounts.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_overtimes', help_text="Admin who approved/rejected overtime")
    overtime_approval_date = models.DateTimeField(null=True, blank=True, help_text="When overtime was approved/rejected")
    overtime_notes = models.TextField(blank=True, help_text="Admin notes about overtime approval/rejection")

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"Attendance for {self.employee} on {self.date}"

    def calculate_overtime_hours(self):
        """Calculate overtime hours based on time worked vs expected daily hours"""
        if self.time_in and self.time_out:
            # Ensure both are datetime objects
            if hasattr(self.time_in, 'total_seconds'):  # Check if it's a timedelta
                return 0
            if hasattr(self.time_out, 'total_seconds'):  # Check if it's a timedelta
                return 0

            # Both should be datetime objects now
            try:
                duration = self.time_out - self.time_in
                hours_worked = duration.total_seconds() / 3600
                expected_daily_hours = float(self.employee.weekly_hours) / 5
                overtime = max(0, hours_worked - expected_daily_hours)
                return round(overtime, 2)
            except (TypeError, AttributeError) as e:
                # If there's still an error, return 0 to prevent crashes
                print(f"Error calculating overtime hours: {e}")
                return 0
        return 0

    def approve_overtime(self, approved_by, notes=""):
        """Approve overtime hours for this attendance record"""
        self.overtime_approved = True
        self.overtime_rejected = False
        self.overtime_approved_by = approved_by
        self.overtime_approval_date = timezone.now()
        self.overtime_notes = notes
        self.save()

    def reject_overtime(self, rejected_by, notes=""):
        """Reject overtime hours for this attendance record"""
        self.overtime_approved = False
        self.overtime_rejected = True
        self.overtime_approved_by = rejected_by
        self.overtime_approval_date = timezone.now()
        self.overtime_notes = notes
        self.save()

    @property
    def overtime_status(self):
        """Get the current overtime approval status"""
        if self.overtime_approved:
            return "approved"
        elif self.overtime_rejected:
            return "rejected"
        elif self.overtime_hours > 0:
            return "pending"
        else:
            return "none"

    def save(self, *args, **kwargs):
        # Calculate overtime hours automatically
        self.overtime_hours = self.calculate_overtime_hours()

        # Update employee's online status based on attendance
        if self.time_in and not self.time_out:
            # Employee clocked in - set as online/working
            self.employee.is_online = True
        elif self.time_out:
            # Employee clocked out - set as offline
            self.employee.is_online = False

        # Save the employee status
        self.employee.save(update_fields=['is_online'])

        super().save(*args, **kwargs)

    @property
    def duration(self):
        """Calculate work duration for this attendance record"""
        if self.time_in and self.time_out:
            duration = self.time_out - self.time_in
            total_minutes = int(duration.total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"
        elif self.time_in:
            # Currently working
            duration = timezone.now() - self.time_in
            total_minutes = int(duration.total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m (ongoing)"
        return "No time recorded"

    @property
    def is_complete(self):
        """Check if both time_in and time_out are recorded"""
        return self.time_in is not None and self.time_out is not None

    @property
    def is_ongoing(self):
        """Check if employee has clocked in but not clocked out"""
        return self.time_in is not None and self.time_out is None
