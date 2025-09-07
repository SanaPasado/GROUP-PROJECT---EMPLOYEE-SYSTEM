from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .forms import ReportForm
from .models import Report


@login_required
def report_create(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_by = request.user  # use request.user, not user
            report.save()
            messages.success(request, 'Report submitted successfully!')
            return redirect('reports:my_reports')  # redirect to user's reports
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

@login_required
def my_reports(request):
    """View for employees to see their own reports"""
    reports = Report.objects.filter(reported_by=request.user)
    return render(request, 'reports/my_reports.html', {'reports': reports})
