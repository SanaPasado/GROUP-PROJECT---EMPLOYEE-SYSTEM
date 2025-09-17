from django.urls import path
from .views import (
    PaycheckNotificationListView,
    PaycheckNotificationDetailView,
    PaycheckNotificationCreateView,
    old_paycheck_dashboard, PaycheckDashboardView,  # Use the function-based dashboard view
)

app_name = 'notifications'

urlpatterns = [
    path('', PaycheckNotificationListView.as_view(), name='employee_notifications'),
    path('create/', PaycheckNotificationCreateView.as_view(), name='create_notification'),
    path('<int:pk>/', PaycheckNotificationDetailView.as_view(), name='notification_detail'),
    path('dashboard/', PaycheckDashboardView.as_view(), name='paycheck_dashboard'),
]
