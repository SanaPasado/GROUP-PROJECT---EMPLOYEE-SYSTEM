from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import PaycheckNotification


@login_required
def employee_notifications(request):
    """Display paycheck notifications for the logged-in employee"""
    try:
        # Since your Employee model is the user model, request.user should work directly
        notifications = PaycheckNotification.objects.filter(
            employee=request.user
        ).order_by('-sent_at')[:20]  # Get latest 20 notifications

        # Count unread notifications BEFORE marking them as read
        unread_count = PaycheckNotification.objects.filter(
            employee=request.user,
            is_read=False
        ).count()

        # Mark notifications as read when viewed (only if there are unread ones)
        if unread_count > 0:
            unread_notifications = notifications.filter(is_read=False)
            unread_notifications.update(is_read=True)

        context = {
            'notifications': notifications,
            'unread_count': unread_count
        }
        return render(request, 'notifications/employee_notifications.html', context)

    except Exception as e:
        messages.error(request, f'An error occurred while loading notifications: {str(e)}')
        return render(request, 'notifications/employee_notifications.html', {
            'notifications': [],
            'unread_count': 0
        })


@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    if request.method == 'POST':
        try:
            notification = get_object_or_404(
                PaycheckNotification,
                id=notification_id,
                employee=request.user
            )
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success'})
        except PaycheckNotification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
