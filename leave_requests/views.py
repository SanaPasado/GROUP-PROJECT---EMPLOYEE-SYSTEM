from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import LeaveRequest
from .forms import LeaveRequestForm, AdminLeaveReviewForm


class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'leave_requests/leave_request_form.html'
    success_url = reverse_lazy('leave_requests:my_leaves')

    def form_valid(self, form):
        form.instance.employee = self.request.user
        messages.success(self.request, 'Your leave request has been submitted successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Request Leave'
        return context


class MyLeavesListView(LoginRequiredMixin, ListView):
    model = LeaveRequest
    template_name = 'leave_requests/employee_leaves.html'
    context_object_name = 'leave_requests'
    paginate_by = 10

    def get_queryset(self):
        return LeaveRequest.objects.filter(employee=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Leave Requests'

        # Calculate status counts for the current user's leave requests
        user_requests = LeaveRequest.objects.filter(employee=self.request.user)
        context['pending_count'] = user_requests.filter(status='pending').count()
        context['approved_count'] = user_requests.filter(status='approved').count()
        context['rejected_count'] = user_requests.filter(status='rejected').count()

        return context


class AdminLeavesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = LeaveRequest
    template_name = 'leave_requests/admin_leaves.html'
    context_object_name = 'leave_requests'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = LeaveRequest.objects.all()
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'All Leave Requests'
        context['pending_count'] = LeaveRequest.objects.filter(status='pending').count()
        context['approved_count'] = LeaveRequest.objects.filter(status='approved').count()
        context['rejected_count'] = LeaveRequest.objects.filter(status='rejected').count()
        context['current_filter'] = self.request.GET.get('status', 'all')
        return context


class LeaveRequestDetailView(LoginRequiredMixin, DetailView):
    model = LeaveRequest
    template_name = 'leave_requests/leave_request_detail.html'
    context_object_name = 'leave_request'

    def get_queryset(self):
        if self.request.user.is_staff:
            return LeaveRequest.objects.all()
        else:
            return LeaveRequest.objects.filter(employee=self.request.user)

    def post(self, request, *args, **kwargs):
        """Handle review form submission from the detail view"""
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to review leave requests.')
            return redirect('leave_requests:my_leaves')

        leave_request = self.get_object()

        if leave_request.status != 'pending':
            messages.error(request, 'This leave request has already been reviewed.')
            return redirect('leave_requests:leave_request_detail', pk=leave_request.pk)

        status = request.POST.get('status')
        admin_comment = request.POST.get('admin_comment', '')

        if status in ['approved', 'rejected']:
            try:
                leave_request.status = status
                leave_request.admin_comment = admin_comment
                leave_request.reviewed_by = request.user
                leave_request.reviewed_at = timezone.now()
                leave_request.save()

                if status == 'approved':
                    # Calculate and show deducted days in success message
                    days_deducted = leave_request.duration_days
                    leave_type = leave_request.get_leave_type_display()

                    if leave_request.leave_type in ['vacation', 'sick']:
                        messages.success(request, f'Leave request has been approved. {days_deducted} {leave_type.lower()} day{"s" if days_deducted != 1 else ""} have been deducted from the employee\'s balance.')
                    else:
                        messages.success(request, 'Leave request has been approved.')
                elif status == 'rejected':
                    messages.warning(request, 'Leave request has been rejected.')

            except ValueError as e:
                # Handle insufficient leave days error
                messages.error(request, f'Cannot approve leave request: {str(e)}')
                return redirect('leave_requests:leave_request_detail', pk=leave_request.pk)
            except Exception as e:
                messages.error(request, f'An error occurred while processing the request: {str(e)}')
                return redirect('leave_requests:leave_request_detail', pk=leave_request.pk)
        else:
            messages.error(request, 'Please select a valid decision.')

        return redirect('leave_requests:leave_request_detail', pk=leave_request.pk)


# Function-based view for quick approval/rejection (AJAX)
@login_required
@user_passes_test(lambda u: u.is_staff)
def quick_review_leave(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')

        if action in ['approved', 'rejected']:
            try:
                leave_request.status = action
                leave_request.admin_comment = comment
                leave_request.reviewed_by = request.user
                leave_request.reviewed_at = timezone.now()
                leave_request.save()

                if action == 'approved':
                    days_deducted = leave_request.duration_days
                    leave_type = leave_request.get_leave_type_display()

                    if leave_request.leave_type in ['vacation', 'sick']:
                        messages.success(request, f'Leave request has been approved. {days_deducted} {leave_type.lower()} day{"s" if days_deducted != 1 else ""} have been deducted from the employee\'s balance.')
                    else:
                        messages.success(request, f'Leave request has been {action}.')
                else:
                    messages.success(request, f'Leave request has been {action}.')

            except ValueError as e:
                messages.error(request, f'Cannot approve leave request: {str(e)}')
            except Exception as e:
                messages.error(request, f'An error occurred while processing the request: {str(e)}')

    return redirect('leave_requests:admin_leaves')
