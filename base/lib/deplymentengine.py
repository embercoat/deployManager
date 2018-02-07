# coding=utf-8
import hashlib
import logging
from base.lib.helpers import bytesToString
from base.lib.scanner import Scanner
from base.models import Artifact, ApplicationServer, Deployment, Task


class DeploymentEngine():
    logger = logging.getLogger("base.lib.deploymentengine")

    def deploy(self, artifactID, appServerID, task=None):
        arti = Artifact.objects.get(pk=artifactID)
        self.logger.info("Scanning appserver to work from fresh data")
        if task: task.running().log("Scanning appserver to work from fresh data")

        Scanner().scanAppserver(appServerID)

        appServ = ApplicationServer.objects.get(pk=appServerID)
        appServClient = appServ.getClient()

        dep = Deployment.objects.filter(artifact=arti, applicationServer=appServ)
        if dep.exists():
            if task: task.log("Artifact already deployed. returning without deployment").complete()
            self.logger.info("Artifact already deployed. returning without deployment")
            return {"success": False,
                        "message": "Requested artifact {} already deployed on {}".format(arti, appServ)}
        else:
            if task: task.log("Not trying to redeploy current deployment. Continuing")
            self.logger.info("Not trying to redeploy current deployment. Continuing")

            currentDeployments = Deployment.objects.filter(
                artifact__in=Artifact.objects.filter(
                    artifactid=arti.artifactid,
                    groupid=arti.groupid
                ),
                applicationServer=appServ
            )
            if (len(currentDeployments)):
                if task: task.log("There is a known deployment matching what we want to deploy. ")
                self.logger.info("There is a known deployment matching what we want to deploy.")
                for cd in currentDeployments:
                    self.logger.info("Undeploying {}".format(cd.runtimeName))
                    if task: task.log("Undeploying {}".format(cd.runtimeName))
                    appServClient.undeploy(cd.runtimeName)
                    cd.delete()

            deploymentBytes = arti.download()
            if not arti.sha1:
                sha1 = hashlib.sha1()
                sha1.update(deploymentBytes)
                bytes = bytesToString(sha1.digest())
                arti.sha1 = bytes
                arti.save()

                if task: task.log("Deploying {} to {}".format(arti, appServ))
                self.logger.info("Deploying {} to {}".format(arti, appServ))
            appServClient.deploy(deploymentBytes, arti.runtimeName())
            newDeployment = Deployment(artifact=arti, applicationServer=appServ, runtimeName=arti.runtimeName())
            newDeployment.save()
            if task: task.log("Successfully deployed {} to {}".format(arti, appServ)).complete()
            return {"success": True, "message": "Successfully deployed {} to {}".format(arti, appServ)}

    def undeploy(self, deployment, task=None):
        if task: task.running().log("Trying to undeploy {}".format(deployment))
        self.logger.info("trying to undeploy")
        try:
            deployment = Deployment.objects.get(pk=deployment)
            deployment.undeploy()
            deployment.delete()
            message = "Successfully undeployed {} from {}".format(deployment.artifact, deployment.applicationServer)
            if task: task.log(message).complete()
            return {"success": True, "message": message}
        except:
            if task: task.log("Deployment does not exist").complete()
            return {"success": False, "message": "Deployment does not exist"}
