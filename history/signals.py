from django.db.models.signals import pre_save
from django.dispatch import receiver
from accounts.models import Employee
from .models import EmployeeHistory
from crum import get_current_user  # handy package to get current logged-in user


@receiver(pre_save, sender=Employee)
def track_employee_updates(sender, instance, **kwargs):
    if not instance.pk:  # Skip creation, only track updates
        return

    try:
        old_instance = Employee.objects.get(pk=instance.pk)
    except Employee.DoesNotExist:
        return

    user = get_current_user()

    # Loop through fields to detect changes
    for field in instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name)
        new_value = getattr(instance, field_name)

        if old_value != new_value:
            EmployeeHistory.objects.create(
                employee=instance,
                updated_by=user if user and user.is_authenticated else None,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
            )
