from django.shortcuts import render, redirect
from django.urls import reverse
from django_otp.decorators import otp_required

from accounts.forms import RegisterForm, LoginForm, OTPVerifyForm
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
import base64
from io import BytesIO
import qrcode
from django_otp.plugins.otp_totp.models import TOTPDevice

User = get_user_model()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def register_page(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return render(request, "403.html", status=403)

    form = RegisterForm(request.POST or None, request.FILES or None)
    context = {"form": form}

    if form.is_valid():
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data["password"])
        new_user.save()
        return redirect("emp_management:employees")

    return render(request, "auth/register.html", context)

def user_manual(request):
    return render(request, 'login/user_manual.html')

def login_page(request):
    form = LoginForm(request.POST or None)
    context = {'form': form}

    if form.is_valid():
        user = form.cleaned_data["user"]
        current_ip = get_client_ip(request)

        # Check if the user has a 2FA device set up
        has_2fa = TOTPDevice.objects.filter(user=user).exists()

        if not has_2fa or user.last_login_ip == current_ip:
            # If 2FA is not set up, or if the IP is the same, log them in directly.
            user.last_login_ip = current_ip
            user.save()
            login(request, user)
            return redirect('emp_management:employees')
        else:
            # IP has changed AND they have 2FA, so we must verify.
            # We log them in to a temporary session to remember who they are.
            login(request, user)
            return redirect('accounts:otp_verify')

    return render(request, 'login/login.html', context)

def logout_view(request):
    logout(request)
    return redirect(reverse('accounts:login_page'))

@login_required
def otp_setup(request):
    """This view handles the ONE-TIME setup of a 2FA device."""
    device, created = TOTPDevice.objects.get_or_create(user=request.user, name='default')

    # Only show the QR code when it's first created.
    if created:
        uri = device.config_url
        img = qrcode.make(uri)
        buf = BytesIO()
        img.save(buf, format='PNG')
        qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        context = {'qr_b64': qr_b64}
        return render(request, 'login/otp_setup.html', context)
    else:
        # If they have already set up a device, just redirect them.
        return redirect('emp_management:employees')

@login_required
def otp_verify(request):
    """This view handles the verification of a 6-digit code during login."""
    if not request.user.is_authenticated:
        return redirect('accounts:login_page')

    # This view should NEVER show the QR code.
    # It only verifies the token.
    form = OTPVerifyForm(request.POST or None, user=request.user)

    if request.method == 'POST':
        if form.is_valid():
            otp_code = form.cleaned_data.get("otp_code")
            # Use the form's verification method
            if form.verify_otp(request.user, otp_code):
                # On successful OTP, update the last login IP.
                request.user.last_login_ip = get_client_ip(request)
                request.user.save()
                return redirect('emp_management:employees')
            else:
                form.add_error('otp_code', 'Invalid OTP code')

    context = {'form': form}
    return render(request, 'login/otp_verify.html', context)
