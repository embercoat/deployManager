# coding=utf-8
from django.utils import timezone
from django.utils.module_loading import import_string

from base.models import ApplicationServer, Deployment, Artifact, Repository
from base.lib.helpers import base64ToString, GAV


class Scanner():

    def searchReposBySHA1(self, sha1):
        for repo in Repository.objects.all():
            repoClient = repo.getClient()
            print("searching for {} in {}".format(sha1, repo.url))
            try:
                result = repoClient.findArtifactBySHA1(sha1)
                result['repository'] = repo.pk
                return result
            except FileNotFoundError:
                pass

        raise FileNotFoundError

    def searchReposByCoordinates(self, groupid, artifactid, version):
        result = []
        for repo in Repository.objects.all():
            repoClient = repo.getClient()
            print("searching for {}:{}:{} in {}".format(groupid, artifactid, version, repo.url))
            try:
                artifacts = repoClient.findArtifactByCoordinates(groupid, artifactid, version)
                for a in artifacts:
                    dbArtifact = Artifact.objects.filter(
                        groupid=a['groupid'],
                        artifactid=a['artifactid'],
                        version=a['version'],
                        extension=a['extension']
                    )
                    if dbArtifact.exists():
                        a['id'] = dbArtifact[0].pk
                    else:
                        newArtifact = Artifact(
                            groupid=a['groupid'],
                            artifactid=a['artifactid'],
                            version=a['version'],
                            extension=a['extension'],
                            repository=repo
                        )
                        newArtifact.save()
                        a['id'] = newArtifact.pk


                result.append(
                    {
                        "repository" : {
                            "id" : repo.pk,
                            "name" : repo.__str__()
                        },
                        "artifacts" : artifacts
                    }
                )

            except FileNotFoundError:
                # This allows the search to continue in other repos.
                pass
        if len(result) == 0:
            raise FileNotFoundError
        else:
            return result


    def scanAppserver(self, appServerId):
        appServData = ApplicationServer.objects.get(pk=appServerId)

        appServClient = appServData.getClient()
        deployments = appServClient.getDeployments()
        for deployment in deployments.json()['result']:
            print(deployment['result']['name'])
            sha1 = base64ToString(deployment['result']['content'][0]['hash']['BYTES_VALUE'])
            artifact = Artifact()
            try:
                artifact = Artifact.objects.get(sha1__iexact=sha1)
                print("artifact in db. no need to search for it")


            except Artifact.DoesNotExist:
                print("SHA1 not in db. searching for details")
                try:
                    result = self.searchReposBySHA1(sha1)
                    print("Found in {}".format(result['repository']))

                    artifact.repository_id = result['repository']
                    artifact.extension = result['extension']
                    artifact.artifactid = result['artifactId']
                    artifact.version = result['version']
                    artifact.groupid = result['groupId']
                    artifact.sha1 = sha1
                    artifact.save()


                except FileNotFoundError:
                    print("SHA1 not found in any repo")

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
                releases = rep.getClient().findVersions(a)
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
