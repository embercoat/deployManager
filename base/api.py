# coding=utf-8
import hashlib
import json

from django.http import HttpResponse, HttpResponseNotFound
from django.views import View

from base.lib.deplymentengine import DeploymentEngine
from base.lib.helpers import bytesToString
from base.lib.scanner import Scanner
from base.models import Artifact, ApplicationServer, Deployment


class API(View):
    template_name = 'base/index.html'

    def get(self, request, category, action, object=None):
        response = {}
        scanner = Scanner()
        if request.body:
            body = json.loads(request.body)
        else:
            body = {}
        """
            Functions and endpoints
        """

        if response == {}:
            response = { "success" : False, "message" : "Method does not exist" }
        if response["success"]:
            return HttpResponse(json.dumps(response))
        else:
            return HttpResponseNotFound(json.dumps(response))

    def post(self, request, category, action, object=None):
        if request.body:
            body = json.loads(request.body)
        else:
            body = {}
        response = {}
        scanner = Scanner()

        if category == "search":
            if action == "artifact":
                if not hasattr(body, "version"):
                    body["version"] = ""

                response = {"success": True,
                 "result" : scanner.searchReposByCoordinates(body['groupid'], body['artifactid'], body["version"])
                }

        if category == "scans":
            if action == "scan":
                if object:
                    response = scanner.scanAppserver(object)
                else:
                    response = scanner.scanAllAppservers()
            if action == "checkForNewReleases":
                response = scanner.checkForNewReleases()


        if category == "deploy":
            de = DeploymentEngine()
            if action == "deploy":
                response = de.deploy(body["artifactPK"], body['appServerPK'])


            if action == "undeploy":
                response = de.undeploy(body['deployment'])

        if response == {}:
            response = { "success" : False, "message" : "Method does not exist" }


        if response["success"]:
            r = HttpResponse(json.dumps(response))
        else:
            r = HttpResponseNotFound(json.dumps(response))

        r["Content-Type"] = "application/json"
        return r