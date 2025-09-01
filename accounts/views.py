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

        if user.last_login_ip  == current_ip:
            # IP is the same, no OTP required
            user.last_login_ip = current_ip
            user.save()
            login(request, user)
            return redirect('emp_management:employees')
        else:
            # IP has changed, require OTP
            user.last_login_ip = current_ip
            user.save()
            login(request, user)
            return redirect('accounts:otp_verify')

    return render(request, 'login/login.html', context)


def logout_view(request):
    logout(request)
    return redirect(reverse('accounts:login_page'))


def otp_verify(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login_page')

    device, _ = TOTPDevice.objects.get_or_create(user=request.user)
    uri = device.config_url
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    form = OTPVerifyForm(request.POST or None, user=request.user)

    if request.method == 'POST':
        if form.is_valid():
            otp_code = form.cleaned_data.get("otp_code")
            if form.verify_otp(request.user, otp_code):
                request.session['otp_verified'] = True
                return redirect('emp_management:employees')
            else:
                form.add_error('otp_code', 'Invalid OTP code')

    context = {
        'form': form,
        'qr_b64': qr_b64,
    }
    return render(request, 'login/otp_verify.html', context)
