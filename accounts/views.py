from django.shortcuts import render, redirect
from django_otp.decorators import otp_required

from accounts.forms import RegisterForm, LoginForm, OTPVerifyForm
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
import base64
from io import BytesIO
import qrcode
from django_otp.plugins.otp_totp.models import TOTPDevice
User = get_user_model()

@login_required
def register_page(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect("home")

    form = RegisterForm(request.POST or None, request.FILES or None)
    context = {"form": form}

    if form.is_valid():
        new_user = form.save(commit=False)  # don't save yet
        new_user.set_password(form.cleaned_data["password"])  # hash password
        new_user.save()  # now save to DB
        return redirect("employees")

    return render(request, "auth/register.html", context)
def login_page(request):
    form = LoginForm(request.POST or None)
    context = {
        'form': form}

    if form.is_valid():
        user = form.cleaned_data["user"]
        login(request, user)
        return redirect("accounts:otp_verify")
    #user is used instead of email and password because
    # we used 'cleaned_data = user' in forms and user = authenticate

    return render(request, 'login/login.html', context)


def otp_verify(request):
    # Logic for secret key and QR code generation
    device, _ = TOTPDevice.objects.get_or_create(user=request.user)
    uri = device.config_url
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Logic for verifying the OTP code
    form = OTPVerifyForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            otp_code = form.cleaned_data.get("otp_code")
            # Call the custom method defined on the form to verify the OTP.
            if form.verify_otp(request.user, otp_code):
                request.session['otp_verified'] = True
                return redirect('employees')
            else:
                form.add_error('otp_code', 'Invalid OTP code')

    context = {
        'form': form,
        'qr_b64': qr_b64,
    }
    return render(request, 'login/totp_setup.html', context)

