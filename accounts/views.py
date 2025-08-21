from django.shortcuts import render, redirect
from accounts.forms import RegisterForm, LoginForm
from django.contrib.auth import get_user_model, login, authenticate

User = get_user_model()

def register_page(request):
    form = RegisterForm(request.POST or None)
    context = {
        'form': form}

    if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            newUser = User.objects.create_user(first_name, last_name, email, password)

            login(request, newUser)
            return redirect("home")

    return render(request, 'auth/register.html', context)

def login_page(request):
    form = LoginForm(request.POST or None)
    context = {
        'form': form}

    if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

    user = authenticate(request, username=email, password=password)
#do i still need this if i have it in forms already
    return render(request, 'login/login.html', context)


