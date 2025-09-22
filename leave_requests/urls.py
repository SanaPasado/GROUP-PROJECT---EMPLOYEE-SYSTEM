from django.urls import path
from .views import (
    LeaveRequestListView,
    LeaveRequestCreateView,
    LeaveRequestDetailView,
    AdminLeaveRequestsView,
    LeaveRequestReviewView,
    leave_request_stats,
)

app_name = 'leave_requests'

urlpatterns = [
    # Employee URLs
    path('', LeaveRequestListView.as_view(), name='my_leaves'),
    path('create/', LeaveRequestCreateView.as_view(), name='create_leave'),
    path('<int:pk>/', LeaveRequestDetailView.as_view(), name='leave_detail'),

    # Admin URLs
    path('admin/', AdminLeaveRequestsView.as_view(), name='admin_leaves'),
    path('admin/<int:pk>/review/', LeaveRequestReviewView.as_view(), name='review_leave'),
    path('api/stats/', leave_request_stats, name='leave_stats'),
]
