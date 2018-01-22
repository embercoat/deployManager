# coding=utf-8
from django.utils import timezone
from django.utils.module_loading import import_string

from base.models import ApplicationServer, Deployment, Artifact, Repository
from base.lib.helpers import bytesToString, GAV


class Scanner():

    def searchReposBySHA1(self, sha1):
        for repo in Repository.objects.all():
            repoClient = import_string(repo.type)(repo.url, repo.username, repo.password)
            print("searching for {} in {}".format(sha1, repo.url))
            try:
                return { "repo" : repo.pk, "gav" : repoClient.findBySHA1(sha1)}
            except FileNotFoundError:
                pass

        raise FileNotFoundError

    def scanAppserver(self, appServerId):
        appServData = ApplicationServer.objects.get(pk=appServerId)

        appServClient = appServData.getClient()
        deployments = appServClient.getDeployments()
        for deployment in deployments.json()['result']:
            print(deployment['result']['name'])
            sha1 = bytesToString(deployment['result']['content'][0]['hash']['BYTES_VALUE'])
            artifact = Artifact()
            try:
                artifact = Artifact.objects.get(sha1__iexact=sha1)
                print("artifact in db. no need to search for it")
                try:
                    dep = Deployment.objects.get(artifact_id=artifact.pk, applicationServer_id=appServerId)
                    print("Deployment known. Not doing anything")

                except Deployment.DoesNotExist:
                    print("Deployment not known. Adding")
                    dep = Deployment(
                        artifact_id=artifact.pk,
                        applicationServer_id=appServerId,
                        detected=timezone.now(),
                        runtimeName=deployment['result']['name']
                    )
                    dep.save()

            except Artifact.DoesNotExist:
                print("SHA1 not in db. searching for details")
                try:
                    result = self.searchReposBySHA1(sha1)
                    print("Found in {}".format(result['repo']))
                    gav = result['gav']
                    artifact.fromGAV(gav)
                    artifact.repository_id = result['repo']
                    artifact.sha1 = sha1
                    artifact.save()


                except FileNotFoundError:
                    print("SHA1 not found in any repo")

        # Touch the databse object to update the timestamp
        appServData.save()
        print("Scanned {}".format(appServData))

        return {"success": True, "message": "scanned {}".format(appServData.name)}

    def scanAllAppservers(self):
        appServData = ApplicationServer.objects.all()
        print("Scanning All")
        for asd in appServData:
            print("Scanning {}".format(asd.name))
            self.scanAppserver(asd.pk)

        return { "success" : True, "message": "scanned all the things"}

    def checkForNewReleases(self):
        repos = Repository.objects.all()
        knownArtifacts = Artifact.objects.all()
        for rep in repos:
            print("Searching {}".format(rep))
            for a in knownArtifacts:
                print("Searching for {}".format(a))
                releases = rep.getClient().findVersions(a.getGAV())
                print("Found {} newer versions".format(len(releases['versions'])))
                for version in releases['versions']:
                    try:
                        Artifact.objects.get(groupid=a.groupid, artifactid=a.artifactid, version=version)
                        print("Artifact and version exists. Doing nothing")

                    except Artifact.DoesNotExist:
                        # Artifact missing. Add it
                        print("Artifact is missing. Create it in database.")
                        newArtifact = Artifact(groupid=a.groupid, artifactid=a.artifactid, version=version, repository_id=rep.pk)
                        newArtifact.save()

        return { "success" : True, "message": "Updated all the repos"}
