from django.shortcuts import render


def index(request):
    return render(request, 'index.html', {})


def login_page(request):
    return render(request, 'login.html', {})


def register_page(request):
    return render(request, 'register.html', {})


def register_ok(request):
    return render(request, 'register_ok.html', {})


