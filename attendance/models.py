from django.utils import timezone

from django.db import models

# Create your models here.
class Attendance(models.Model):
    employee = models.ForeignKey('accounts.Employee', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time_in = models.TimeField(default=timezone.now)
    time_out = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')
        #para maensure na isa lang record per employee per date
    def __str__(self):
        return f"Attendance for Employee {self.employee} on {self.date}"