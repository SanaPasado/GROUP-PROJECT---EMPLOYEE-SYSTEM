from django.db import models
from django.utils import timezone
from accounts.models import Employee
from django.apps import AppConfig

class PaycheckNotification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='paycheck_notifications')
    message = models.TextField(default="Your paycheck has been sent!")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sent_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    sent_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=50, default="paycheck")

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        if self.employee:
            return f"Paycheck notification for {self.employee.first_name} {self.employee.last_name} - {self.sent_at}"
        return f"Paycheck notification for Unknown - {self.sent_at}"

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
