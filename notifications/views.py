from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse_lazy
from .models import PaycheckNotification
from accounts.models import Employee
from django import forms


class PaycheckNotificationForm(forms.ModelForm):
    class Meta:
        model = PaycheckNotification
        fields = ['employee', 'amount', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow non-staff, non-admin, active employees as recipients
        self.fields['employee'].queryset = Employee.objects.filter(staff=False, admin=False, active=True)


class PaycheckNotificationListView(LoginRequiredMixin, ListView):
    model = PaycheckNotification
    template_name = 'notifications/employee_notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        # Employees only see their own notifications
        return PaycheckNotification.objects.filter(employee=self.request.user).order_by('-sent_at')


class PaycheckNotificationDetailView(LoginRequiredMixin, DetailView):
    model = PaycheckNotification
    template_name = 'notifications/notification_detail.html'
    context_object_name = 'notification'

    def get_queryset(self):
        # Employees can only see their own notifications
        return PaycheckNotification.objects.filter(employee=self.request.user)


class PaycheckNotificationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = PaycheckNotification
    form_class = PaycheckNotificationForm
    template_name = 'notifications/send_paycheck.html'
    success_url = reverse_lazy('notifications:paycheck_dashboard')

    def test_func(self):
        # Only staff/admin can send notifications
        return self.request.user.is_staff or self.request.user.is_superuser or self.request.user.admin

    def form_valid(self, form):
        form.instance.sent_by = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        # Render the form with errors
        return self.render_to_response(self.get_context_data(form=form))


class PaycheckDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'notifications/paycheck_dashboard.html'

    def test_func(self):
        # Only staff/admin can access the dashboard
        return self.request.user.is_staff or self.request.user.is_superuser or self.request.user.admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import Employee

        # Get all active employees with their payroll breakdown
        active_employees = Employee.objects.filter(active=True).order_by('first_name', 'last_name')

        # Calculate payroll breakdown for each employee
        employees_with_payroll = []
        for employee in active_employees:
            payroll_breakdown = employee.calculate_payroll_breakdown()
            employees_with_payroll.append({
                'employee': employee,
                'breakdown': payroll_breakdown,
                'suggested_amount': employee.get_suggested_paycheck_amount()
            })

        context.update({
            'notifications': PaycheckNotification.objects.all().order_by('-sent_at')[:20],
            'active_employees': active_employees,
            'employees_with_payroll': employees_with_payroll,
        })
        return context
