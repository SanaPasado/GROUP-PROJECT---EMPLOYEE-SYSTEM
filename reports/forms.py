from django import forms
from reports.models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['subject', 'description']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the issue...'}),
        }
