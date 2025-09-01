from django.urls import path
from . import views
from .views import my_attendance, record_time, AttendanceListView, AttendanceDetailView
app_name = 'attendance'
urlpatterns = [
    path('', my_attendance, name='my-attendance'),
    path('record/', record_time, name='record_time'),
    path('all/', AttendanceListView.as_view(), name='attendance_list'),
    path('<int:pk>/', AttendanceDetailView.as_view(), name='attendance_detail'),
]
