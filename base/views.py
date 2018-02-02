# coding=utf-8
import hashlib

from django.contrib.auth.decorators import login_required
from django.forms import ChoiceField, forms, ModelChoiceField
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from base.lib.helpers import GAV, base64ToString
from base.models import Repository, ApplicationServer, Artifact, Deployment
from .lib.scanner import Scanner
import json

# Create your views here.
class IndexView(View):
    template_name = 'base/index.html'

    @method_decorator(login_required)
    def get(self, request):
        applicationServers = ApplicationServer.objects.all()

        return render(request, "base/index.html",
                      {
                          "applicationServers" : applicationServers,
                      }
              )

class AppServer(View):

    @method_decorator(login_required)
    def get(self, request, appServ):
        appServObject = ApplicationServer.objects.get(pk=appServ)
        deployments = Deployment.objects.filter(applicationServer=appServObject)
        return render(request, "base/applicationServers.html",
                      {
                          "applicationServer" : appServObject,
                          "deployments" : deployments
                      }
                  )


class DeployView(View):

    @method_decorator(login_required)
    def get(self, request):

        appServers = []
        for appServ in ApplicationServer.objects.all():
            appServers.append({"id" : appServ.pk, "name" : appServ.__str__()})

        return render(request, "base/deploy.html", {
                        "applicationServers": appServers,
                     }
        )