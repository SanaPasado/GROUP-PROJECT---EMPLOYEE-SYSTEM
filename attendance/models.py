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

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"Attendance for {self.employee} on {self.date}"

    def save(self, *args, **kwargs):
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
