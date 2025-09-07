from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import EmployeeHistory

from accounts.models import Employee



class HistoryListView(UserPassesTestMixin, ListView):
    template_name = 'history.html'
    context_object_name = 'histories'
    model = EmployeeHistory

    def test_func(self):
        # This function must return True or False.
        # It checks if the logged-in user is a superuser.
        return self.request.user.is_superuser

