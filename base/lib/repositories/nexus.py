# coding=utf-8
from distutils.version import StrictVersion

import requests
from requests.auth import HTTPBasicAuth
from requests.cookies import RequestsCookieJar

from base.lib.artifactrepository import ArtifactRepository


class RepoNexus(ArtifactRepository):

    _urls = {
        "findBySHA1" : "/service/local/lucene/search?sha1={}",
        "singleUseToken" : "/service/siesta/wonderland/authenticate",
        "login" : "/service/local/authentication/login",
        "findByCoordinates" : "/service/local/lucene/search?g={}&a={}&v={}",
        "getArtifact" : "/service/local/artifact/maven/redirect?r={}&g={}&a={}&v={}&e={}",
    }
    _extensions = [ "ear", "war" ]

    cookies = RequestsCookieJar()

    def __init__(self, url, username, password):
        super().__init__(url, username, password)
        response = self._invoke(self.url + self._urls["login"], {})
        self.cookies = response.cookies
        if not response.status_code == 200:
            """ Reset everything to nothing """
            self.url = ""
            self.username = ""
            self.password = ""
            raise Exception("Invalid credentials")

    def _invoke(self, url, payload={}):
        headers = { "Accept" : "application/json"}

        if payload:
            response = requests.post(url,
                         data=payload,
                         auth=HTTPBasicAuth(self.username, self.password),
                         headers=headers,
                         cookies=self.cookies
            )
        else:
            response = requests.get(url,
                          auth=HTTPBasicAuth(self.username, self.password),
                          headers=headers,
                          cookies=self.cookies
            )
        if response.status_code == 404:
            raise FileNotFoundError()

        if not response.status_code == 200:
            raise Exception("Something went wrong")

        return response

    def getArtifact(self, artifact):
        repo = self.findRepoByCoordinates(artifact)
        artifactResponse = self._invoke(
                                self.url + self._urls["getArtifact"].format(
                                    repo,
                                    artifact.groupid,
                                    artifact.artifactid,
                                    artifact.version,
                                    artifact.extension
                                ))
        return artifactResponse.content

    def findVersions(self, artifact):
        json = self._invoke(self.url + self._urls["findByCoordinates"].format(artifact.groupid, artifact.artifactid, "")).json()
        versions = { "latest" : "0.0.0", "versions" : []}

        for release in json["data"]:
            if not versions["latest"] or StrictVersion(release['latestRelease']) > StrictVersion(versions["latest"]):
                versions["latest"] = release["latestRelease"]

            if StrictVersion(release['version']) > StrictVersion(artifact.version):
                versions["versions"].append(release["version"])
        return versions


    def findRepoByCoordinates(self, artifact):
        response = self._invoke(self.url + self._urls["findByCoordinates"].format(artifact.groupid, artifact.artifactid, artifact.version))
        return response.json()["repoDetails"][0]["repositoryId"]

    def findArtifactByCoordinates(self, groupId, artifactId, version=''):
        response = self._invoke(self.url + self._urls["findByCoordinates"].format(groupId, artifactId, version))

        artifactCollection = []
        for artifact in response.json()['data']:
            artifactCollection.append(
                {
                    "groupid" : artifact["groupId"],
                    "artifactid" : artifact["artifactId"],
                    "version" : artifact["version"],
                    "extension" : self._findExtension(artifact['artifactHits'])
                }
            )

        return artifactCollection

    def _findExtension(self, artifactHit):
        extension = ""
        for link in artifactHit[0]['artifactLinks']:
            if not link['extension'] == 'pom' and 'classifier' not in link:
                extension = link['extension']

        return extension

    def findArtifactBySHA1(self, sha1):
        response = self._invoke(self.url + self._urls["findBySHA1"].format(sha1))
        json = response.json()['data'][0]
        extension = ""
        for hit in json["artifactHits"]:
            extension = self._findExtension(hit)

        return {
                  "groupId" : json["groupId"],
                  "artifactId" : json["artifactId"],
                  "version" : json["version"],
                  "extension" : extension
               }
