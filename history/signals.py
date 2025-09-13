from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from crum import get_current_user
from accounts.models import Employee
from .models import EmployeeHistory

# A dictionary to hold the old state of the instance before it's saved
_old_instance_map = {}

@receiver(pre_save, sender=Employee)
def capture_old_instance(sender, instance, **kwargs):
    """Before an Employee object is saved, capture its current state from the database."""
    if instance.pk:
        try:
            # Store the old instance in our map, keyed by its primary key
            _old_instance_map[instance.pk] = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            # This happens on creation, so there's no old instance to capture
            pass

@receiver(post_save, sender=Employee)
def log_employee_changes(sender, instance, created, **kwargs):
    """After an Employee object is saved, compare its old and new state and log changes."""
    # Don't log anything if the instance was just created
    if created:
        return

    # Retrieve the old instance from our map
    old_instance = _old_instance_map.pop(instance.pk, None)
    if not old_instance:
        return

    # Get the user who made the change
    user = get_current_user()
    if not user or not user.pk: # Check if user is anonymous or not saved
        user = None

    # Define the fields we want to track for changes
    tracked_fields = [
        'first_name', 'last_name', 'position', 'department', 'salary',
        'phone_number', 'address', 'vacation_days', 'sick_leaves'
    ]

    # Compare old and new values for each tracked field
    for field_name in tracked_fields:
        old_value = getattr(old_instance, field_name)
        new_value = getattr(instance, field_name)

        # If a value has changed, create a history record
        if old_value != new_value:
            EmployeeHistory.objects.create(
                employee=instance,
                updated_by=user,
                field_name=field_name.replace('_', ' ').title(), # e.g., 'first_name' -> 'First Name'
                old_value=str(old_value),
                new_value=str(new_value),
            )
