# coding=utf-8
import base64
import importlib

import sys
from django.utils import six


class GAV():
    groupId = ""
    artifactId = ""
    version = ""

    def __init__(self, groupId, artifactId, version):
        self.groupId    = groupId
        self.artifactId = artifactId
        self.version    = version

def bytesToString(b64):
    bytes = base64.b64decode(b64)
    string = ""
    for b in bytes:
        string = string + "{0:02x}".format(b)

    return string