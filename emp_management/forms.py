from django import forms
from accounts.models import Employee

# class EmployeeDetailForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = [
#             'first_name',
#             'last_name',
#             'email',
#             'phone_number',
#             'emergency_contact',
#             'department',
#             'position',
#             'salary',
#             'photo'
#         ]
#         widgets = {
#             'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
#             'last_name': forms.TextInput(attrs={'readonly': 'readonly'}),
#             'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
#             'phone_number': forms.TextInput(attrs={'readonly': 'readonly'}),
#             'emergency_contact': forms.NumberInput(attrs={'readonly': 'readonly'}),
#             'department': forms.TextInput(attrs={'readonly': 'readonly'}),
#             'position': forms.TextInput(attrs={'readonly': 'readonly'}),
#             'salary': forms.NumberInput(attrs={'readonly': 'readonly'}),
#         }

# This form is for the regular user, with restricted editable fields
from django import forms
from accounts.models import Employee

class EmployeeUpdateForm(forms.ModelForm):
    # fields naka disabled kase kapag naka readonly sila,
    # need parin ivalidate ng form and rerquire ka
    # magsend ng bagong data so that fails
    first_name = forms.CharField(disabled=True)
    last_name = forms.CharField(disabled=True)
    email = forms.EmailField(disabled=True)
    department = forms.CharField(disabled=True)
    position = forms.CharField(disabled=True)
    salary = forms.FloatField(disabled=True)

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
            'photo',
        ]


# This form is for the admin, with all fields editable
class AdminEmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        # Add all the fields that you want the admin to be able to edit
        fields = '__all__'