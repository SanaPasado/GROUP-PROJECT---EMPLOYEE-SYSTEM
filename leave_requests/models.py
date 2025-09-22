from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

Employee = get_user_model()


class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('sick', 'Sick Leave'),
        ('vacation', 'Vacation Leave'),
        ('personal', 'Personal Leave'),
        ('emergency', 'Emergency Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Admin response
    reviewed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    admin_comment = models.TextField(blank=True, help_text="Admin's comment on the leave request")
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"

    @property
    def duration_days(self):
        """Calculate the number of days for this leave request"""
        return (self.end_date - self.start_date).days + 1

    def save(self, *args, **kwargs):
        # Set reviewed_at timestamp when status changes from pending
        if self.pk:
            old_status = LeaveRequest.objects.get(pk=self.pk).status
            if old_status == 'pending' and self.status != 'pending':
                self.reviewed_at = timezone.now()
        super().save(*args, **kwargs)
