from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from accounts.models import Employee
from .forms import ReportForm
from .models import Report


@login_required
def report_create(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_by = request.user
            report.save()
            messages.success(request, 'Report submitted successfully!')
            # Redirect based on user type
            if request.user.is_staff or request.user.is_superuser:
                return redirect('reports:employee_reports', slug=request.user.slug)
            else:
                return redirect('emp_management:employee_detail', slug=request.user.slug)
    else:
        form = ReportForm()

    return render(request, 'reports/report_form.html', {'form': form})



def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_staff_or_superuser)
def report_list(request):
    reports = Report.objects.all()
    return render(request, 'reports/report_list.html', {'reports': reports})

# The my_reports view has been removed as it is now redundant.

@login_required
@user_passes_test(is_staff_or_superuser)
def employee_reports(request, slug):
    """View for admins to see reports by a specific employee."""
    employee = get_object_or_404(Employee, slug=slug)
    reports = Report.objects.filter(reported_by=employee)
    context = {
        'reports': reports,
        'employee': employee
    }
    # This view now uses the my_reports.html template for a consistent design.
    return render(request, 'reports/my_reports.html', context)
