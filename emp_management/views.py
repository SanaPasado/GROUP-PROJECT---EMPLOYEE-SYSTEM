from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, DetailView, ListView
from django.urls import reverse_lazy, reverse
from accounts.models import Employee  # import your custom model
from emp_management.forms import EmployeeUpdateForm


class EmpListView(ListView):
    model = Employee
    context_object_name = 'employees' #data inside template
    template_name = 'emp_management/employee_list.html'

    def get_queryset(self):
        # Exclude staff/admin users
        return Employee.objects.filter(staff=False, admin=False)

class EmpDetailView(DetailView):
    model = Employee
    context_object_name = 'employee_detail'
    template_name = 'emp_management/employee_detail.html'

    def get_queryset(self):
        # Exclude staff/admin users
        return Employee.objects.filter(is_staff=False, is_superuser=False)

    def get_object(self):
        return Employee.objects.get(slug=self.kwargs["slug"])

class EmpUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeUpdateForm
    context_object_name = 'employee'   # <--- we rename object → employee
    template_name = 'emp_management/employee_update.html'

    def get_object(self, queryset=None):
        # fetch the employee using slug
        return get_object_or_404(Employee, slug=self.kwargs["slug"])

    def get_success_url(self):
        # after saving, redirect back to detail page
        return reverse('employee_detail', kwargs={'slug': self.object.slug})





# class EmpUpdateView(UpdateView):
#     model = Employee
#     form_class = EmployeeUpdateForm
#     context_object_name = 'employee_update'
#     template_name = 'emp_management/employee_update.html'
#
#     def get_queryset(self):
#         # Exclude staff/admin users
#         return Employee.objects.filter(is_staff=False, is_superuser=False)
#
#     def get_object(self):
#         return Employee.objects.get(slug=self.kwargs["slug"])
#
#     def get_success_url(self):
#         # This redirects to the 'employee-detail' URL,
#         # passing the slug of the object that was just updated.
#         return reverse('employee_detail', kwargs={'slug': self.object.slug})
#





# @method_decorator(login_required, name='dispatch')
# class MyProfileUpdateView(UpdateView):
#     model = Employee
#     fields = ['phone_number', 'emergency_contact', 'photo']
#     template_name = "emp_management/profile_update.html"
#     success_url = reverse_lazy("my-profile")
#
#     def get_object(self):
#         # only allow employee to edit their own record
#         return self.request.user
