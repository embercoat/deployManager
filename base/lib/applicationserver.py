# coding=utf-8


class ApplicationServerAbstract():

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password


    def getDeployments(self):
        pass

    def browseContent(self, name):
        pass

    def getContent(self, name, path):
        pass

    def deploy(self, bytes, name):
        pass

    def undeploy(self, name):
        pass