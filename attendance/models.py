from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

def get_current_date():
    return timezone.now().date()

class Attendance(models.Model):
    employee = models.ForeignKey('accounts.Employee', on_delete=models.CASCADE)
    date = models.DateField(default=get_current_date)
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)

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

    def save(self, *args, **kwargs):
        # Calculate overtime hours if both time_in and time_out exist
        if self.time_in and self.time_out:
            # Create datetime objects for calculation (TimeFields are already in local time)
            time_in_dt = datetime.combine(self.date, self.time_in)
            time_out_dt = datetime.combine(self.date, self.time_out)

            # Handle case where time_out is past midnight (next day)
            if self.time_out < self.time_in:
                time_out_dt += timedelta(days=1)

            # Calculate total hours worked
            duration = time_out_dt - time_in_dt
            total_hours = duration.total_seconds() / 3600

            # Get expected daily hours from employee's weekly hours (weekly_hours / 5 days)
            expected_daily_hours = float(self.employee.weekly_hours) / 5 if self.employee.weekly_hours else 8.0

            # Calculate overtime hours
            if total_hours > expected_daily_hours:
                self.overtime_hours = round(total_hours - expected_daily_hours, 2)
            else:
                self.overtime_hours = 0.00

        super().save(*args, **kwargs)
