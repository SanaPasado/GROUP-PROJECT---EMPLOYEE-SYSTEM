from django.contrib import admin
from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'leave_type', 'created_at']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Leave Details', {
            'fields': ('employee', 'leave_type', 'start_date', 'end_date', 'reason')
        }),
        ('Review', {
            'fields': ('status', 'reviewed_by', 'admin_comment', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
