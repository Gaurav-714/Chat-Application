from django.shortcuts import render

def registerView(request):
    return render(request, 'signup.html')

def loginView(request):
    return render(request, 'signin.html')