# coding=utf-8
import hashlib
import json

from django.http import HttpResponse, HttpResponseNotFound
from django.views import View

from base.lib.helpers import bytesToString
from base.lib.scanner import Scanner
from base.models import Artifact, ApplicationServer, Deployment


class API(View):
    template_name = 'base/index.html'

    def get(self, request, category, action, object=None):
        response = {}
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
        body = json.loads(request.body)
        response = {}
        if category == "scans":
            scanner = Scanner()
            if action == "scan":
                if object:
                    response = scanner.scanAppserver(object)
                else:
                    response = scanner.scanAllAppservers()
            if action == "checkForNewReleases":
                response = scanner.checkForNewReleases()


        if category == "deploy":
            if action == "deploy":
                arti = Artifact.objects.get(pk=body["artifactPK"])
                print("Scanning appserver to work from fresh data")
                Scanner().scanAppserver(body["appServerPK"])
                appServ = ApplicationServer.objects.get(pk=body["appServerPK"])
                appServClient = appServ.getClient()

                try:
                    Deployment.objects.get(artifact=arti)
                    response = { "success" : False, "message" : "Requested artifact {} already deployed on {}".format(arti, appServ)}
                    print("Artifact already deployed. returning without deployment")
                except:
                    print("Not trying to redeploy current deployment. Continuing")

                    currentDeployments = Deployment.objects.filter(
                        artifact__in=Artifact.objects.filter(
                            artifactid=arti.artifactid,
                            groupid=arti.groupid
                        )
                    )
                    if(len(currentDeployments)):
                        print("There is a known deployment matching what we want to deploy.")
                        for cd in currentDeployments:
                            print("Undeploying {}".format(cd.runtimeName))
                            appServClient.undeploy(cd.runtimeName)
                            cd.delete()

                    deploymentBytes = arti.download()
                    if not arti.sha1:
                        sha1 = hashlib.sha1()
                        sha1.update(deploymentBytes)
                        bytes = bytesToString(sha1.digest())
                        arti.sha1 = bytes
                        arti.save()

                    print("Deploying {} to {}".format(arti, appServ))
                    appServClient.deploy(deploymentBytes, arti.runtimeName())
                    newDeployment = Deployment(artifact=arti, applicationServer=appServ, runtimeName=arti.runtimeName())
                    newDeployment.save()
                    response = {"success": True, "message": "Successfully deployed {} to {}".format(arti, appServ)}

            if action == "undeploy":
                try:
                    deployment = Deployment.objects.get(pk=body['deployment'])
                    deployment.undeploy()
                    deployment.delete()
                except:
                    response = {"success": False, "message": "Deployment does not exist"}

        if response == {}:
            response = { "success" : False, "message" : "Method does not exist" }


        if response["success"]:
            r = HttpResponse(json.dumps(response))
        else:
            r = HttpResponseNotFound(json.dumps(response))

        r["Content-Type"] = "application/json"
        return r