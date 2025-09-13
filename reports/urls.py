from django.urls import path
from .views import report_create, report_list, employee_reports

app_name = 'reports'
urlpatterns = [
    path('create/', report_create, name='report_create'),
    path('list/', report_list, name='report_list'),
    # The my-reports URL has been removed.
    path('employee/<slug:slug>/', employee_reports, name='employee_reports'),


]
