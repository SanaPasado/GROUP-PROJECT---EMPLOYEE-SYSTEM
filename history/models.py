from django.db import models
from django.conf import settings

class EmployeeHistory(models.Model):
    employee = models.ForeignKey("accounts.Employee", on_delete=models.CASCADE, related_name="history")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} | {self.field_name} updated by {self.updated_by} at {self.updated_at}"
