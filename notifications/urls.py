from django.urls import path
from .views import (
    PaycheckNotificationListView,
    PaycheckNotificationDetailView,
    PaycheckNotificationCreateView,
    PaycheckDashboardView,
    get_employee_payroll_data,
)

app_name = 'notifications'

urlpatterns = [
    path('', PaycheckNotificationListView.as_view(), name='employee_notifications'),
    path('create/', PaycheckNotificationCreateView.as_view(), name='create_notification'),
    path('<int:pk>/', PaycheckNotificationDetailView.as_view(), name='notification_detail'),
    path('dashboard/', PaycheckDashboardView.as_view(), name='paycheck_dashboard'),
    path('ajax/employee/<int:employee_id>/payroll/', get_employee_payroll_data, name='get_employee_payroll_data'),
]
