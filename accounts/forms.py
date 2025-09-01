from django import forms
from django.contrib.auth import get_user_model, authenticate
from django_otp.plugins.otp_totp.models import TOTPDevice

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


class OTPVerifyForm(forms.Form):
    """
    Form for verifying a Time-based One-Time Password (TOTP).
    """
    otp_code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "OTP Code"}),
        label="One-Time Password",
        required=True
    )
    def __init__(self, *args, **kwargs):
        # This line is key! It grabs the user object.
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def verify_otp(self, user, otp_code):
        """
        Verifies the OTP code against the user's TOTP device.

        Args:
            user: The user object.
            otp_code: The OTP code to verify.

        Returns:
            bool: True if the OTP is valid, False otherwise.
        """
        # Get the user's OTP device (assuming one per user)
        try:
            device = TOTPDevice.objects.get(user=user)
            # Use the verify_token method from the django_otp library
            return device.verify_token(otp_code)
        except TOTPDevice.DoesNotExist:
            return False


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
            'emergency_contact',
            'photo',
            'sick_leaves',
            'vacation_days',
            'work_schedule',
            'address',


        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', "placeholder": "First Name"}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', "placeholder": "Last Name"}),
            'email': forms.EmailInput(attrs={'class': 'form-control', "placeholder": "Email"}),
            'position': forms.TextInput(attrs={'class': 'form-control', "placeholder": "Position"}),
            'department': forms.TextInput(attrs={'class': 'form-control', "placeholder": "Department"}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', "placeholder": "Salary"}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control', "placeholder": "Phone Number"}),
            'emergency_contact': forms.NumberInput(attrs={'class': 'form-control', "placeholder": "Emergency Contact"}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', "placeholder": "Address"}),
            'sick_leaves': forms.NumberInput(attrs={'class': 'form-control', "placeholder": "Sick Leaves"}),
            'vacation_days': forms.NumberInput(attrs={'class': 'form-control', "placeholder": "Vacation Days"}),
            'work_schedule': forms.TextInput(attrs={'class': 'form-control' , "placeholder": "Work Schedule"}),
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