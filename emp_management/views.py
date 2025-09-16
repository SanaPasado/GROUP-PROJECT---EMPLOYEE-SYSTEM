from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, DetailView, ListView, DeleteView
from django.urls import reverse_lazy, reverse
from accounts.models import Employee  # import your custom model
from emp_management.forms import EmployeeUpdateForm, AdminEmployeeUpdateForm


class EmpListView(LoginRequiredMixin, ListView):
    model = Employee
    context_object_name = 'employees'
    template_name = 'emp_management/employee_list.html'

    def get_queryset(self):
        # kase nakikita yung admins sa list view i don wan dat
        queryset = Employee.objects.filter(staff=False, admin=False)
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(slug__icontains=query) |
                Q(position__icontains=query) |
                Q(department__icontains=query))
        return queryset



class EmpDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    context_object_name = 'employee_detail'
    template_name = 'emp_management/employee_detail.html'

    def get_object(self):
        return Employee.objects.get(slug=self.kwargs["slug"])

class EmpUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Employee
    form_class = EmployeeUpdateForm
    context_object_name = 'employee'   # <--- we rename object → employee
    template_name = 'emp_management/employee_update.html'

    def test_func(self):
        # Get the employee object that the user is trying to update
        employee_to_update = self.get_object()
        # Allow access if the current user is a staff member OR if they are updating their own profile
        return self.request.user.is_staff or self.request.user == employee_to_update

    def get_object(self, queryset=None):
        return get_object_or_404(Employee, slug=self.kwargs["slug"])

    def form_valid(self, form):
        try:
            self.object = form.save()
            return redirect(self.get_success_url())
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            form.add_error('photo', 'There was an error uploading the photo. Please try again.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        return super().form_invalid(form)
    #this is for debugging

    def get_form_class(self):
        if self.request.user.is_staff:
            print("✅ Using ADMIN form")
            return AdminEmployeeUpdateForm
        print("✅ Using EMPLOYEE form")
        return EmployeeUpdateForm

    def get_success_url(self):
        # after saving, redirect back to detail page
        return reverse('emp_management:employee_detail', kwargs={'slug': self.object.slug})



class EmpDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    context_object_name = 'employee'
    template_name = 'emp_management/employee_delete.html'
    success_url = reverse_lazy('emp_management:employees')
    #
    # def test_func(self):
    #     return self.request.user.is_staff or self.request.user.is_superuser



#function for polling
@login_required
def get_employee_statuses(request):
    employees = Employee.objects.all().values('slug', 'is_online')
    statuses = {emp['slug']: emp['is_online'] for emp in employees}
    return JsonResponse(statuses)

@staff_member_required
def send_individual_paycheck(request, slug):
    """Send paycheck notification to individual employee"""
    employee = get_object_or_404(Employee, slug=slug)

    if request.method == 'POST':
        amount = request.POST.get('amount', '')
        message = request.POST.get('message', 'Your paycheck has been sent!')

        # Use the employee model method to send notification
        employee.send_paycheck_notification(
            amount=float(amount) if amount else None,
            message=message,
            notification_type="paycheck",  # Always set to paycheck
            sent_by=request.user
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Paycheck notification sent to {employee.get_full_name()}'
        })

    context = {
        'employee': employee,
    }
    return render(request, 'emp_management/send_paycheck_notification.html', context)

@staff_member_required
def paycheck_dashboard(request):
    """Dashboard for managing paycheck notifications"""
    from notifications.models import PaycheckNotification

    if request.method == 'POST':
        # Handle form submission for sending paycheck notification
        employee_id = request.POST.get('employee_id')
        amount = request.POST.get('amount', '')
        message = request.POST.get('message', 'Your paycheck has been sent!')
        notification_type = request.POST.get('notification_type', 'paycheck')

        try:
            employee = Employee.objects.get(id=employee_id)

            # Send the notification using the employee model method
            employee.send_paycheck_notification(
                amount=float(amount) if amount else None,
                message=message,
                notification_type=notification_type,
                sent_by=request.user
            )

            return JsonResponse({
                'status': 'success',
                'message': f'Paycheck notification sent to {employee.get_full_name()}'
            })

        except Employee.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Employee not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while sending the notification'
            })

    # GET request - display the dashboard
    # Get recent notifications
    recent_notifications = PaycheckNotification.objects.select_related('employee', 'sent_by').order_by('-sent_at')[:10]

    # Get all active employees for the form
    active_employees = Employee.objects.filter(active=True).order_by('first_name', 'last_name')

    # Get statistics
    total_employees = Employee.objects.filter(active=True).count()
    total_notifications = PaycheckNotification.objects.count()
    unread_notifications = PaycheckNotification.objects.filter(is_read=False).count()

    context = {
        'recent_notifications': recent_notifications,
        'active_employees': active_employees,
        'total_employees': total_employees,
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'notification_types': [
            ('paycheck', 'Paycheck Sent'),
            ('bonus', 'Bonus Payment'),
            ('salary_adjustment', 'Salary Adjustment'),
        ]
    }
    return render(request, 'emp_management/paycheck_dashboard.html', context)

@staff_member_required
def admin_panel(request):
    """
    A view for the admin panel, accessible only to staff members.
    """
    return render(request, 'emp_management/admin_panel.html')
