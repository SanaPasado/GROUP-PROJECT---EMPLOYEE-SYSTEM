from django.utils import timezone
from django.db import models


class Attendance(models.Model):
    employee = models.ForeignKey('accounts.Employee', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"Attendance for {self.employee} on {self.date}"
