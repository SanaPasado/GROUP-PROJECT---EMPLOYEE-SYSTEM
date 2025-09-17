from django.db import models
from django.contrib.auth.models import User

from Employee_System import settings


class Report(models.Model):
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Report from {self.reported_by.first_name} {self.reported_by.last_name}: {self.subject[:50]}...'
