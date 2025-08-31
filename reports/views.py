from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test

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
            return redirect('emp_management:employees')  # adjust to your url name
    else:
        form = ReportForm()

    return render(request, 'reports/report_form.html', {'form': form})




def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def report_list(request):
    reports = Report.objects.all()
    return render(request, 'reports/report_list.html', {'reports': reports})
