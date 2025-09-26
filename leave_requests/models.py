from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

Employee = get_user_model()


class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('sick', 'Sick Leave'),
        ('vacation', 'Vacation Leave'),
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
            old_instance = LeaveRequest.objects.get(pk=self.pk)
            old_status = old_instance.status

            # If status changes from pending to approved, deduct leave days
            if old_status == 'pending' and self.status == 'approved':
                self.reviewed_at = timezone.now()
                self._deduct_leave_days()
            elif old_status == 'pending' and self.status == 'rejected':
                self.reviewed_at = timezone.now()
            # If status changes from approved back to pending/rejected, restore leave days
            elif old_status == 'approved' and self.status != 'approved':
                self._restore_leave_days()
        super().save(*args, **kwargs)

    def _deduct_leave_days(self):
        """Deduct leave days from employee's balance when leave is approved"""
        days_to_deduct = self.duration_days
        employee = self.employee

        if self.leave_type == 'vacation' and employee.vacation_days is not None:
            if employee.vacation_days >= days_to_deduct:
                employee.vacation_days -= days_to_deduct
                employee.save(update_fields=['vacation_days'])
            else:
                raise ValueError(f"Insufficient vacation days. Available: {employee.vacation_days}, Required: {days_to_deduct}")

        elif self.leave_type == 'sick' and employee.sick_leaves is not None:
            if employee.sick_leaves >= days_to_deduct:
                employee.sick_leaves -= days_to_deduct
                employee.save(update_fields=['sick_leaves'])
            else:
                raise ValueError(f"Insufficient sick leave days. Available: {employee.sick_leaves}, Required: {days_to_deduct}")

    def _restore_leave_days(self):
        """Restore leave days to employee's balance when approved leave is reverted"""
        days_to_restore = self.duration_days
        employee = self.employee

        if self.leave_type == 'vacation' and employee.vacation_days is not None:
            employee.vacation_days += days_to_restore
            employee.save(update_fields=['vacation_days'])

        elif self.leave_type == 'sick' and employee.sick_leaves is not None:
            employee.sick_leaves += days_to_restore
            employee.save(update_fields=['sick_leaves'])
