from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings


def sign_up(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmpassword")
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("sign-up")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("sign-up")
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()
        
        messages.success(request, "Account created successfully. Check your email for activation link.")
        return redirect("sign-in")
    
    return render(request, "signup.html")


def sign_in(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("dashboard") 
            else:
                messages.error(request, "Your account is not activated. Check your email for the activation link.")
        else:
            messages.error(request, "Invalid email or password.")
        
        return redirect("sign-in")
    
    return render(request, "signin.html")