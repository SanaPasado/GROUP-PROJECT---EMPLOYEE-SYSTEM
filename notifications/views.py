from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PaycheckNotification


@login_required
def employee_notifications(request):
    """Display paycheck notifications for the logged-in employee"""
    notifications = PaycheckNotification.objects.filter(
        employee=request.user
    ).order_by('-sent_at')[:20]  # Get latest 20 notifications

    # Mark notifications as read when viewed
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)

    context = {
        'notifications': notifications,
        'unread_count': PaycheckNotification.objects.filter(
            employee=request.user,
            is_read=False
        ).count()
    }
    return render(request, 'notifications/employee_notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    if request.method == 'POST':
        try:
            notification = PaycheckNotification.objects.get(
                id=notification_id,
                employee=request.user
            )
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success'})
        except PaycheckNotification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
