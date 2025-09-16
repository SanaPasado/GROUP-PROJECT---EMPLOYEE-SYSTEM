from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import PaycheckNotification
from accounts.models import Employee


@admin.register(PaycheckNotification)
class PaycheckNotificationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'notification_type', 'amount', 'sent_at', 'is_read', 'sent_by']
    list_filter = ['notification_type', 'is_read', 'sent_at']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__email']
    readonly_fields = ['sent_at', 'sent_by']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'employee':
            # Exclude staff and admin users from being selected as recipients
            kwargs["queryset"] = Employee.objects.filter(staff=False, admin=False, active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:  # Only set sent_by for new notifications
            obj.sent_by = request.user
        super().save_model(request, obj, form, change)


class EmployeeNotificationAdmin(admin.ModelAdmin):
    list_display = ['email', 'get_full_name', 'department', 'paycheck_actions']
    search_fields = ['first_name', 'last_name', 'email', 'department']
    list_filter = ['department', 'staff', 'active']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-paycheck-notification/',
                 self.admin_site.admin_view(self.send_paycheck_notification),
                 name='send_paycheck_notification'),
            path('<int:employee_id>/send-individual-paycheck/',
                 self.admin_site.admin_view(self.send_individual_paycheck),
                 name='send_individual_paycheck'),
        ]
        return custom_urls + urls

    def paycheck_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Send Paycheck Notification</a>',
            reverse('admin:send_individual_paycheck', args=[obj.pk])
        )
    paycheck_actions.short_description = 'Paycheck Actions'

    def send_individual_paycheck(self, request, employee_id):
        employee = Employee.objects.get(id=employee_id)

        if request.method == 'POST':
            amount = request.POST.get('amount', '')
            custom_message = request.POST.get('message', 'Your paycheck has been sent!')
            notification_type = request.POST.get('notification_type', 'paycheck')

            # Create notification
            PaycheckNotification.objects.create(
                employee=employee,
                notification_type=notification_type,
                message=custom_message,
                amount=amount if amount else None,
                sent_by=request.user
            )

            messages.success(request, f'Paycheck notification sent to {employee.get_full_name()}')
            return HttpResponseRedirect(reverse('admin:accounts_employee_changelist'))

        context = {
            'employee': employee,
            'title': f'Send Paycheck Notification to {employee.get_full_name()}',
            'opts': Employee._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/send_paycheck_notification.html', context)

    def send_paycheck_notification(self, request):
        if request.method == 'POST':
            employee_ids = request.POST.getlist('employee_ids')
            amount = request.POST.get('amount', '')
            custom_message = request.POST.get('message', 'Your paycheck has been sent!')
            notification_type = request.POST.get('notification_type', 'paycheck')

            employees = Employee.objects.filter(id__in=employee_ids, active=True)

            notifications = []
            for employee in employees:
                notifications.append(PaycheckNotification(
                    employee=employee,
                    notification_type=notification_type,
                    message=custom_message,
                    amount=amount if amount else None,
                    sent_by=request.user
                ))

            PaycheckNotification.objects.bulk_create(notifications)
            messages.success(request, f'Paycheck notifications sent to {len(employees)} employees')
            return HttpResponseRedirect(reverse('admin:accounts_employee_changelist'))

        employees = Employee.objects.filter(active=True).order_by('first_name', 'last_name')
        context = {
            'employees': employees,
            'title': 'Send Paycheck Notifications',
            'opts': Employee._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/bulk_send_paycheck.html', context)

    actions = ['send_bulk_paycheck_notification']

    def send_bulk_paycheck_notification(self, request, queryset):
        selected_ids = queryset.values_list('id', flat=True)
        return HttpResponseRedirect(
            f"{reverse('admin:send_paycheck_notification')}?ids={','.join(map(str, selected_ids))}"
        )
    send_bulk_paycheck_notification.short_description = "Send paycheck notifications to selected employees"
