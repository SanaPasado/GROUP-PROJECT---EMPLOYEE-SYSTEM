from django.db.models import Q

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, DetailView, ListView, DeleteView
from django.urls import reverse_lazy, reverse
from accounts.models import Employee  # import your custom model
from emp_management.forms import EmployeeUpdateForm, AdminEmployeeUpdateForm


class EmpListView(ListView):
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



class EmpDetailView(DetailView):
    model = Employee
    context_object_name = 'employee_detail'
    template_name = 'emp_management/employee_detail.html'

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
        return reverse('employee_detail', kwargs={'slug': self.object.slug})

class EmpDeleteView(DeleteView):
    model = Employee
    context_object_name = 'employee'
    template_name = 'emp_management/employee_delete.html'
    success_url = reverse_lazy('employees')
    #im not sure if it bases on employees in urls.py
    #or what u put on the context object name of list view


