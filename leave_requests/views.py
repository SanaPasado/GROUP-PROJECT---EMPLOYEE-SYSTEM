from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import LeaveRequest
from .forms import LeaveRequestForm, LeaveRequestAdminForm


class LeaveRequestListView(LoginRequiredMixin, ListView):
    model = LeaveRequest
    template_name = 'leave_requests/employee_leaves.html'
    context_object_name = 'leave_requests'
    paginate_by = 10

    def get_queryset(self):
        # Regular employees only see their own requests
        if not self.request.user.is_staff:
            return LeaveRequest.objects.filter(employee=self.request.user)
        # Staff see all requests
        return LeaveRequest.objects.all()


class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'leave_requests/leave_request_form.html'
    success_url = reverse_lazy('leave_requests:my_leaves')

    def form_valid(self, form):
        form.instance.employee = self.request.user
        messages.success(self.request, 'Your leave request has been submitted successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class LeaveRequestDetailView(LoginRequiredMixin, DetailView):
    model = LeaveRequest
    template_name = 'leave_requests/leave_request_detail.html'
    context_object_name = 'leave_request'

    def get_queryset(self):
        # Employees can only view their own requests, staff can view all
        if self.request.user.is_staff:
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(employee=self.request.user)
from django import forms

class AdminLeaveRequestsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = LeaveRequest
    template_name = 'leave_requests/admin_leaves.html'
    context_object_name = 'leave_requests'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = LeaveRequest.objects.all()
        status_filter = self.request.GET.get('status', '')

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['pending_count'] = LeaveRequest.objects.filter(status='pending').count()
        context['approved_count'] = LeaveRequest.objects.filter(status='approved').count()
        context['rejected_count'] = LeaveRequest.objects.filter(status='rejected').count()
        return context


class LeaveRequestReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = LeaveRequest
    form_class = LeaveRequestAdminForm
    template_name = 'leave_requests/leave_request_review.html'
    success_url = reverse_lazy('leave_requests:admin_leaves')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        # Set the reviewer
        form.instance.reviewed_by = self.request.user

        # Add success message based on status
        status = form.cleaned_data['status']
        employee_name = form.instance.employee.get_full_name()

        if status == 'approved':
            messages.success(self.request, f'Leave request for {employee_name} has been approved.')
        elif status == 'rejected':
            messages.success(self.request, f'Leave request for {employee_name} has been rejected.')
        else:
            messages.info(self.request, f'Leave request for {employee_name} status updated.')

        return super().form_valid(form)


@login_required
def leave_request_stats(request):
    """API endpoint for leave request statistics"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)

    stats = {
        'total': LeaveRequest.objects.count(),
        'pending': LeaveRequest.objects.filter(status='pending').count(),
        'approved': LeaveRequest.objects.filter(status='approved').count(),
        'rejected': LeaveRequest.objects.filter(status='rejected').count(),
    }

    return JsonResponse(stats)
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import LeaveRequest


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Please provide detailed reason for your leave request...'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            # Check if start date is not in the past
            if start_date < timezone.now().date():
                raise ValidationError("Start date cannot be in the past.")

            # Check if end date is after start date
            if end_date < start_date:
                raise ValidationError("End date must be after start date.")

            # Check if leave duration is reasonable (max 90 days)
            if (end_date - start_date).days > 90:
                raise ValidationError("Leave duration cannot exceed 90 days.")

        return cleaned_data


class LeaveRequestAdminForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['status', 'admin_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Add your comment (optional)...'}),
        }
