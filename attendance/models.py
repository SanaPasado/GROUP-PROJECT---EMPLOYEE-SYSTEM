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

    def save(self, *args, **kwargs):
        # Simply save without timezone manipulation since timezone.now() already returns timezone-aware datetime
        super().save(*args, **kwargs)
