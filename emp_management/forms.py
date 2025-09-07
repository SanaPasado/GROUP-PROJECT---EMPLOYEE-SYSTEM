
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
    address = forms.CharField(disabled=True)
    sick_leaves = forms.IntegerField(disabled=True)
    vacation_days = forms.IntegerField(disabled=True)
    date_hired = forms.DateField(disabled=True)
    work_schedule= forms.IntegerField(disabled=True)

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
            'address',
            'sick_leaves',
            'vacation_days',
            'work_schedule',
            'date_hired',
        ]


# This form is for the admin, with all fields editable except readonly
class AdminEmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        first_name = forms.CharField(
            widget=forms.TextInput(attrs={'readonly': 'readonly'})
        )
        last_name = forms.CharField(
            widget=forms.TextInput(attrs={'readonly': 'readonly'})
        )
        email = forms.EmailField(
            widget=forms.EmailInput(attrs={'readonly': 'readonly'})
        )
        address = forms.CharField(
            widget=forms.TextInput(attrs={'readonly': 'readonly'})
        )
        sick_leaves = forms.IntegerField(
            widget=forms.NumberInput(attrs={'readonly': 'readonly'})
        )
        vacation_days = forms.IntegerField(
            widget=forms.NumberInput(attrs={'readonly': 'readonly'})
        )
        date_hired = forms.DateField(
            widget=forms.DateInput(attrs={'readonly': 'readonly'})
        )
        work_schedule = forms.IntegerField(
            widget=forms.NumberInput(attrs={'readonly': 'readonly'})
        )
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
            'address',
            'sick_leaves',
            'vacation_days',
            'work_schedule',

        ]


