# coding=utf-8
import json
import urllib
import requests
from requests.auth import HTTPDigestAuth
from urllib.parse import urlencode

from ..applicationserver import ApplicationServerAbstract


class Wildfly11(ApplicationServerAbstract):

    def __init__(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password


    def _invoke(self, command, streamAsResponse = False):
        urlParams = {}
        if streamAsResponse:
            urlParams["useStreamAsResponse"] = ""

        header = {"Content-Type" : "application/json"}

        return requests.post(self.address +'/management?'+urlencode(urlParams),
                             data=json.dumps(command),
                             headers=header,
                             auth=HTTPDigestAuth(self.username, self.password)
                             )

    def getDeployments(self):
        get_deployments = {
            "operation": "read-resource",
            "address": {"deployment": "*"},
            "json.pretty": 1
        }
        return self._invoke(get_deployments)

    def browseContent(self, name):
        browse_content = {
            "operation": "browse-content",
            "address": {"deployment": name},
            "json.pretty": 1
        }

        return self._invoke(browse_content)

    def getContent(self, deployment, path):
        get_pom = {
            "operation": "read-content",
            "path": path,
            "address": {"deployment": deployment},
            "json.pretty": 1
        }
        return self._invoke(get_pom, True)

    def undeploy(self, deployment):
        removeArtifact = { "address" : [{"deployment" : deployment}], "operation" : "remove" }
        self._invoke(removeArtifact)

        command = {"operation": "undeploy", "address": [{"deployment": deployment}]}
        self._invoke(command=command)

    def deploy(self, bytes, name):
        file = { "file" : (name, bytes, 'application/octet-stream') }
        uploadResponse = requests.post(self.address + '/management/add-content',
                             auth=HTTPDigestAuth(self.username, self.password),
                             files=file
                         )

        hash = uploadResponse.json()["result"]["BYTES_VALUE"]

        deployArtifact = { "content" : [{"hash" : {"BYTES_VALUE" : hash}}], "address" : [{"deployment" : name}], "operation" : "add", "enabled" : "true" }
        return self._invoke(deployArtifact)

