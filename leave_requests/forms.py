from django import forms
from django.utils import timezone
from .models import LeaveRequest


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please provide a reason for your leave request...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to today
        today = timezone.now().date()
        self.fields['start_date'].widget.attrs['min'] = today.strftime('%Y-%m-%d')
        self.fields['end_date'].widget.attrs['min'] = today.strftime('%Y-%m-%d')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date must be after or equal to start date.")

            # Check if dates are in the past
            if start_date < timezone.now().date():
                raise forms.ValidationError("Start date cannot be in the past.")

        return cleaned_data


class AdminLeaveReviewForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['status', 'admin_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add your comment about this leave request...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove 'pending' from status choices for admin review
        self.fields['status'].choices = [
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ]
