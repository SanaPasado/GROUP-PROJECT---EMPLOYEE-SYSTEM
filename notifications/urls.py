from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.employee_notifications, name='employee_notifications'),
    path('mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
]
