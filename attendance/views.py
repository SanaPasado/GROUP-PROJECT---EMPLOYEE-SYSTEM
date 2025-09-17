from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.db.models import Q

from .models import Attendance

# Helper: staff check
def is_staff(user):
    return user.is_staff


@login_required
def my_attendance(request):
    today = date.today()
    user = request.user

    try:
        record = Attendance.objects.get(employee=user, date=today)
        has_timed_in = True
        has_timed_out = bool(record.time_out)
    except Attendance.DoesNotExist:
        record = None
        has_timed_in = False
        has_timed_out = False

    records = Attendance.objects.filter(employee=user).order_by('-date')[:10]
    if request.user.is_staff:
        return redirect('attendance:attendance_list')
    else:
        return render(request, 'attendance/my_attendance.html', {
            'has_timed_in': has_timed_in,
            'has_timed_out': has_timed_out,
            'records': records
    })


@login_required
def record_time(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        today = date.today()
        user = request.user

        if action == 'in':
            if Attendance.objects.filter(employee=user, date=today).exists():
                messages.error(request, "You have already timed in today.")
            else:
                Attendance.objects.create(employee=user, date=today, time_in=timezone.now().time())
                messages.success(request, "Time In recorded successfully.")

        elif action == 'out':
            try:
                attendance = Attendance.objects.get(employee=user, date=today)
                if attendance.time_out:
                    messages.error(request, "You have already timed out today.")
                else:
                    attendance.time_out = timezone.now().time()
                    attendance.save()
                    messages.success(request, "Time Out recorded successfully.")
            except Attendance.DoesNotExist:
                messages.error(request, "You haven't timed in yet.")

    return redirect('attendance:my-attendance')


# Staff-only list view
@method_decorator([login_required, user_passes_test(is_staff)], name='dispatch')
class AttendanceListView(ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendance_records'
    paginate_by = 20

    def get_queryset(self):
        queryset = Attendance.objects.select_related('employee').order_by('-date')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(employee__first_name__icontains=query) |
                Q(employee__last_name__icontains=query) |
                Q(employee__department__icontains=query) |
                Q(employee__position__icontains=query)
            )
        return queryset


# Staff-only detail view
@method_decorator([login_required, user_passes_test(is_staff)], name='dispatch')
class AttendanceDetailView(DetailView):
    model = Attendance
    template_name = 'attendance/attendance_detail.html'
    context_object_name = 'record'
