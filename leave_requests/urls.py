from django.urls import path
from . import views

app_name = 'leave_requests'

urlpatterns = [
    # Employee URLs
    path('request/', views.LeaveRequestCreateView.as_view(), name='leave_request_create'),
    path('my-leaves/', views.MyLeavesListView.as_view(), name='my_leaves'),
    path('<int:pk>/', views.LeaveRequestDetailView.as_view(), name='leave_request_detail'),

    # Admin URLs
    path('admin/', views.AdminLeavesListView.as_view(), name='admin_leaves'),
    path('admin/quick-review/<int:pk>/', views.quick_review_leave, name='quick_review_leave'),
]
