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
from datetime import datetime, timedelta
from django.utils import timezone


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


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser or u.admin)
def get_employee_payroll_data(request, employee_id):
    """AJAX endpoint to get employee payroll breakdown with overtime approval logic"""
    try:
        employee = get_object_or_404(Employee, id=employee_id, active=True)

        # Get date range from request or default to current week
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            # Default to current week
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)

        # Get payroll breakdown with overtime approval logic
        breakdown = employee.calculate_payroll_breakdown(start_date, end_date)

        # Check if paycheck already sent for this period
        paycheck_already_sent = employee.has_paycheck_sent_for_period(start_date, end_date)

        # Get pending overtime hours
        pending_overtime = employee.get_pending_overtime_hours(start_date, end_date)

        response_data = {
            'id': employee.id,
            'name': employee.get_full_name(),
            'position': employee.position,
            'department': employee.department,
            'photo': employee.photo.url if employee.photo else None,
            'hourly_rate': str(breakdown['hourly_rate']),
            'overtime_rate': str(breakdown['overtime_rate']),
            'weekly_hours': str(employee.weekly_hours),
            'regular_hours': breakdown['regular_hours'],
            'overtime_hours': breakdown['approved_overtime_hours'],  # Only approved overtime
            'total_overtime_hours': breakdown['total_overtime_hours'],  # All overtime for reference
            'unapproved_overtime_hours': breakdown['unapproved_overtime_hours'],
            'pending_overtime_hours': float(pending_overtime),
            'regular_pay': str(breakdown['regular_pay']),
            'overtime_pay': str(breakdown['overtime_pay']),  # Only from approved overtime
            'total_earnings': str(breakdown['total_pay']),  # Only includes approved overtime
            'period_start': start_date.strftime('%Y-%m-%d'),
            'period_end': end_date.strftime('%Y-%m-%d'),
            'paycheck_already_sent': paycheck_already_sent,
            'has_pending_overtime': pending_overtime > 0,
        }

        return JsonResponse(response_data)

    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


