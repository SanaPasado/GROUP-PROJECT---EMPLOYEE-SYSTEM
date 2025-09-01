from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from emp_management.views import EmpListView, EmpDetailView, EmpUpdateView, EmpDeleteView, get_employee_statuses

app_name = 'emp_management'
urlpatterns = [
    path('', EmpListView.as_view(), name='employees'),

    path("employees/<slug:slug>/", EmpDetailView.as_view(), name="employee_detail"),

    path("employees/<slug:slug>/update",  EmpUpdateView.as_view(), name="employee_update"),

    path("employees/<slug:slug>/delete", EmpDeleteView.as_view(), name="employee_delete"),

    path('api/employee-statuses/', get_employee_statuses, name='employee_statuses'),

]