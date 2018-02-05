# coding=utf-8
import hashlib

from base.lib.helpers import bytesToString
from base.lib.scanner import Scanner
from base.models import Artifact, ApplicationServer, Deployment


class DeploymentEngine():

    def deploy(self, artifactID, appServerID):
        arti = Artifact.objects.get(pk=artifactID)
        print("Scanning appserver to work from fresh data")
        Scanner().scanAppserver(appServerID)
        appServ = ApplicationServer.objects.get(pk=appServerID)
        appServClient = appServ.getClient()

        dep = Deployment.objects.filter(artifact=arti, applicationServer=appServ)
        if dep.exists():
            response = {"success": False,
                        "message": "Requested artifact {} already deployed on {}".format(arti, dep.applicationserver)}
            print("Artifact already deployed. returning without deployment")
        else:
            print("Not trying to redeploy current deployment. Continuing")

            currentDeployments = Deployment.objects.filter(
                artifact__in=Artifact.objects.filter(
                    artifactid=arti.artifactid,
                    groupid=arti.groupid
                ),
                applicationServer=appServ
            )
            if (len(currentDeployments)):
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
            return {"success": True, "message": "Successfully deployed {} to {}".format(arti, appServ)}

    def undeploy(self, deployment):
        print("trying to undeploy")
        try:
            deployment = Deployment.objects.get(pk=deployment)
            message = "Successfully undeployed {} from {}".format(deployment.artifact, deployment.applicationServer)
            deployment.undeploy()
            deployment.delete()
            response = {"success": True, "message": message}
        except:
            response = {"success": False, "message": "Deployment does not exist"}

        return response