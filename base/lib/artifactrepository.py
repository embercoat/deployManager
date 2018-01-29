# coding=utf-8


class ArtifactRepository():

    VERSIONS_ALL = "ALL"
    VERSIONS_LATEST = "LATEST"

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password


    def findArtifactBySHA1(self, sha1):
        pass

    def findByCoordinates(self, groupId, artifactId, version='ALL'):
        pass

    def getArtifact(self, gav):
        pass

    def findLatestVesion(self, groupId, artifactId):
        pass

    @staticmethod
    def getRepositoryProvider(name):
        for c in ArtifactRepository.__subclasses__():
            if name == c.__module__ + "." + c.__name__:
                return c