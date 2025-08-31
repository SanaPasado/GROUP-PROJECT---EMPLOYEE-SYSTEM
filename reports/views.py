from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Report


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    fields = ['subject', 'description']
    template_name = 'reports/report_form.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        # Automatically set the reported_by field to the current user
        form.instance.reported_by = self.request.user
        return super().form_valid(form)


class ReportListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Report
    context_object_name = 'reports'
    template_name = 'reports/report_list.html'

    def test_func(self):
        # Only allow staff members to view the report list
        return self.request.user.is_staff
