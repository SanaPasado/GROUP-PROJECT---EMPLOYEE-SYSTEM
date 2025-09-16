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
    salary = forms.FloatField(disabled=True, widget=forms.NumberInput(attrs={'step': '0.01'}))
    address = forms.CharField(disabled=True)
    sick_leaves = forms.IntegerField(disabled=True)
    vacation_days = forms.IntegerField(disabled=True)
    date_hired = forms.DateField(disabled=True)
    work_schedule = forms.IntegerField(disabled=True)


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
            'date_hired',
            'work_schedule',

        ]


# This form is for the admin, with all fields editable except readonly
class AdminEmployeeUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make specific fields readonly for admin form
        self.fields['first_name'].widget.attrs['readonly'] = True
        self.fields['last_name'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['address'].widget.attrs['readonly'] = True
        self.fields['sick_leaves'].widget.attrs['readonly'] = True
        self.fields['vacation_days'].widget.attrs['readonly'] = True
        self.fields['date_hired'].widget.attrs['readonly'] = True
        self.fields['work_schedule'].widget.attrs['readonly'] = True

        # Add step attribute to salary field for decimal precision
        self.fields['salary'].widget.attrs['step'] = '0.01'
        self.fields['salary'].widget.attrs['placeholder'] = '0.00'

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
        ]
