from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        return render(request, "accounts/login.html")


    def post(self, request):
        print(request)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            loggedin = login(request, user)
            return redirect("/")



        else:
            print("NOT logged in")
            return render(request, "accounts/login.html")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/accounts/login/")