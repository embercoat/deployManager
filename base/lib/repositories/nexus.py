# coding=utf-8
from distutils.version import StrictVersion

import requests
from requests.auth import HTTPBasicAuth
from requests.cookies import RequestsCookieJar

from base.lib.helpers import GAV
from base.lib.artifactrepository import ArtifactRepository

class RepoNexus(ArtifactRepository):

    _urls = {
        "findBySHA1" : "/service/local/lucene/search?sha1={}",
        "singleUseToken" : "/service/siesta/wonderland/authenticate",
        "login" : "/service/local/authentication/login",
        "findByGAV" : "/service/local/lucene/search?g={}&a={}&v={}",
        "getArtifact" : "/service/local/artifact/maven/redirect?r={}&g={}&a={}&v={}&e=war",
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

    def getArtifact(self, gav):
        repo = self.findRepoByCoordinates(gav)
        artifact = self._invoke(self.url + self._urls["getArtifact"].format(repo, gav.groupId, gav.artifactId, gav.version))
        return artifact.content

    def findVersions(self, gav):
        json = self._invoke(self.url + self._urls["findByGAV"].format(gav.groupId, gav.artifactId, "")).json()
        versions = { "latest" : "0.0.0", "versions" : []}

        for release in json["data"]:
            if not versions["latest"] or StrictVersion(release['latestRelease']) > StrictVersion(versions["latest"]):
                versions["latest"] = release["latestRelease"]

            if StrictVersion(release['version']) > StrictVersion(gav.version):
                versions["versions"].append(release["version"])
        return versions


    def findRepoByCoordinates(self, gav):
        response = self._invoke(self.url + self._urls["findByGAV"].format(gav.groupId, gav.artifactId, gav.version))
        return response.json()["repoDetails"][0]["repositoryId"]

    def findBySHA1(self, sha1):
        response = self._invoke(self.url + self._urls["findBySHA1"].format(sha1))
        json = response.json()['data'][0]
        return GAV(json["groupId"], json["artifactId"], json["version"])

