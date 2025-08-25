from django.shortcuts import render, redirect
from accounts.forms import RegisterForm, LoginForm
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required

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
        return redirect("employees")
    #user is used instead of email and password because
    # we used 'cleaned_data = user' in forms and user = authenticate

    return render(request, 'login/login.html', context)


