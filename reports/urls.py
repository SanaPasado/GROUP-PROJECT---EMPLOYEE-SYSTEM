from django.urls import path
from .views import report_create, report_list, my_reports

app_name = 'reports'
urlpatterns = [
    path('create/', report_create, name='report_create'),
    path('list/', report_list, name='report_list'),

    path('my-reports/', my_reports, name='my_reports')


]
