from django.db import models
from django.utils import timezone

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
        # from django.utils import timezone
        #
        # # Ensure time_in and time_out are timezone-aware
        # if self.time_in and timezone.is_naive(self.time_in):
        #     # If time_in is naive (no timezone info), make it timezone-aware
        #     self.time_in = timezone.make_aware(self.time_in, timezone.get_current_timezone())
        #
        # if self.time_out and timezone.is_naive(self.time_out):
        #     # If time_out is naive (no timezone info), make it timezone-aware
        #     self.time_out = timezone.make_aware(self.time_out, timezone.get_current_timezone())
        #
        # # Calculate overtime hours if both time_in and time_out exist
        # if self.time_in and self.time_out and not self.overtime_hours:
        #     # Calculate total hours worked
        #     duration = self.time_out - self.time_in
        #     total_hours = duration.total_seconds() / 3600
        #
        #     # Assuming 8 hours is a standard work day
        #     standard_hours = 8.0
        #     if total_hours > standard_hours:
        #         self.overtime_hours = round(total_hours - standard_hours, 2)
        #     else:
        #         self.overtime_hours = 0.00

        super().save(*args, **kwargs)
