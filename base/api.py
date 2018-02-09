# coding=utf-8
import hashlib
import json
import _thread
import logging
from django.core import serializers

from django.http import HttpResponse, HttpResponseNotFound
from django.views import View

from base.lib.deplymentengine import DeploymentEngine
from base.lib.helpers import bytesToString
from base.lib.scanner import Scanner
from base.models import Artifact, ApplicationServer, Deployment, Task, TaskLog


class API(View):
    logger = logging.getLogger("base.lib.deploymentengine")
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

        if category == "task":
            if action == "fullTask":
                task = Task.objects.get(pk=body['taskID'])
                taskLog = TaskLog.objects.filter(task=task)

                response = { "success" : True,
                             "task" : json.loads(serializers.serialize("json",[task, ])[1:-1]),
                             "log" : json.loads(serializers.serialize("json",taskLog))
                          }
            if action == "logSince":
                task = Task.objects.get(pk=body['taskID'])
                taskLog = TaskLog.objects.filter(task=task, pk__gt=body["logID"])
                response = { "success" : True,
                             "log" : json.loads(serializers.serialize("json", taskLog))
                             }

            if action == "status":
                task = Task.objects.get(pk=body['taskID'])
                response = { "success" : True, "status" : task.status}


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
                self.logger.info("Starting deploymentthread")
                task = Task(title="Deployment", owner=request.user)
                task.save()
                _thread.start_new_thread(de.deploy, (),
                                         {"artifactID" : body["artifactPK"], "appServerID" : body['appServerPK'], "task" :task}
                                     )
                response = { "success" : True, "message" : "deployment accepted", "task" : task.pk }

            if action == "undeploy":
                task = Task(title="Undeployment", owner=request.user)
                task.save()
                _thread.start_new_thread(de.undeploy, (),
                                         {"deployment": body['deployment'],
                                          "task": task})
                response = { "success" : True, "message" : "undeployment accepted", "task" : task.pk }

        if response == {}:
            response = { "success" : False, "message" : "Method does not exist" }


        if response["success"]:
            r = HttpResponse(json.dumps(response))
        else:
            r = HttpResponseNotFound(json.dumps(response))

        r["Content-Type"] = "application/json"
        return r