from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View



class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if "username" in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                r = login(request, user)
                print(r)

                # Redirect to a success page.
                #return HttpResponseRedirect(request.GET['next'])
            else:
                pass
                # Return an 'invalid login' error message.
        else:
            return render(request, "accounts/login.html")