from django.urls import path
from .views import ReportCreateView, ReportListView

app_name = 'reports'
urlpatterns = [
    path('create/', ReportCreateView.as_view(), name='report_create'),
    path('', ReportListView.as_view(), name='report_list'),
]
