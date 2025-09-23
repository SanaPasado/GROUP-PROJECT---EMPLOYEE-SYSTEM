from django.db import models
from django.utils import timezone
from accounts.models import Employee
from django.apps import AppConfig
from datetime import timedelta

class PaycheckNotification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='paycheck_notifications')
    message = models.TextField(default="Your paycheck has been sent!")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sent_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    sent_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=50, default="paycheck")

    # Add fields to track the paycheck period
    week_start_date = models.DateField(null=True, blank=True)
    week_end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-sent_at']
        # Prevent duplicate paychecks for the same employee and week
        unique_together = ['employee', 'week_start_date', 'week_end_date', 'notification_type']

    def __str__(self):
        if self.employee:
            return f"Paycheck notification for {self.employee.first_name} {self.employee.last_name} - {self.sent_at}"
        return f"Paycheck notification for Unknown - {self.sent_at}"

    @classmethod
    def has_paycheck_for_week(cls, employee, start_date, end_date):
        """Check if a paycheck has already been sent for this employee and week"""
        return cls.objects.filter(
            employee=employee,
            week_start_date=start_date,
            week_end_date=end_date,
            notification_type="paycheck"
        ).exists()

    @classmethod
    def get_current_week_dates(cls):
        """Get the start and end dates of the current week (Monday to Sunday)"""
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday
        return start_of_week, end_of_week
