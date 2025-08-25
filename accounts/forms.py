from django import forms
from django.contrib.auth import get_user_model, authenticate

from accounts.models import Employee

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   "placeholder": "email"}))

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   "placeholder": "password"}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password")
            cleaned_data["user"] = user  # store the authenticated user we will use this in views
        return cleaned_data





class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            "placeholder": "Password"
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            "placeholder": "Confirm Password"
        })
    )

    class Meta:
        model = Employee
        fields = [
            'first_name',
            'last_name',
            'email',
            'position',
            'department',
            'salary',
            'phone_number',
            'date_hired',
            'emergency_contact',
            'photo',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', "placeholder": "First Name"}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', "placeholder": "Last Name"}),
            'email': forms.EmailInput(attrs={'class': 'form-control', "placeholder": "Email"}),
            'position': forms.TextInput(attrs={'class': 'form-control', "placeholder": "Position"}),
            'department': forms.TextInput(attrs={'class': 'form-control', "placeholder": "Department"}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', "placeholder": "Salary"}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control', "placeholder": "Phone Number"}),
            'date_hired': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'emergency_contact': forms.NumberInput(attrs={'class': 'form-control', "placeholder": "Emergency Contact"}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }



    def clean_email(self):
        email = self.cleaned_data['email']
        foo = User.objects.filter(email=email)
        if foo.exists():
            raise forms.ValidationError('Email already exists')
        return email


    def clean(self):
        data = self.cleaned_data
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError('Passwords do not match')
        return data

    def save(self, commit=True):
        # Save the Employee instance first
        employee = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:
            employee.set_password(password)  # This is the crucial line for hashing the password!

        if commit:
            employee.save()
        return employee