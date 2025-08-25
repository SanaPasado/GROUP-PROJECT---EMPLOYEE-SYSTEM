from django import forms
from accounts.models import Employee

class EmployeeDetailForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'emergency_contact',
            'department',
            'position',
            'salary',
            'photo'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'phone_number': forms.TextInput(attrs={'readonly': 'readonly'}),
            'emergency_contact': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'department': forms.TextInput(attrs={'readonly': 'readonly'}),
            'position': forms.TextInput(attrs={'readonly': 'readonly'}),
            'salary': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }
class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'phone_number',
            'emergency_contact',
            'department',
            'position',
            'photo'
        ]