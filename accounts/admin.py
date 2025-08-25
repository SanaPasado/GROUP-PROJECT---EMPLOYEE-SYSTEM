from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, UserAdmin
from .models import Employee
User = get_user_model()

admin.site.register(Employee)