# Create your models here.
from distutils.version import StrictVersion

import django
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.module_loading import import_string

from base.lib.artifactrepository import ArtifactRepository
from base.lib.helpers import GAV
from base.lib.repositories import *
from base.lib.applicationserver import ApplicationServerAbstract
from base.lib.applicationservers import *
from django.db import models

repoProviders = []
applicationServers = []

for c in ArtifactRepository.__subclasses__():
    repoProviders.append((c.__module__ + "." + c.__name__, c.__name__))

for c in ApplicationServerAbstract.__subclasses__():
    applicationServers.append((c.__module__ + "." + c.__name__, c.__name__))


class Repository(models.Model):

    def __str__(self):
        return self.name

    url = models.URLField(help_text="schema://adress:port/(path)")
    name = models.CharField(max_length=40)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=repoProviders)
    lastScanned = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name", )

    def getClient(self):
        return import_string(self.type)(self.url, self.username, self.password)

class ApplicationServer(models.Model):

    url = models.URLField(help_text="schema://adress:port/(path)")
    name = models.CharField(max_length=40)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=applicationServers)
    lastScanned = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name", )

    def __str__(self):
        return self.name

    def getClient(self):
        return import_string(self.type)(self.url, self.username, self.password)

class Artifact(models.Model):

    def __str__(self):
        return "{}:{}:{}".format(self.groupid, self.artifactid, self.version)

    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    groupid = models.CharField(max_length=50)
    artifactid = models.CharField(max_length=50)
    version = models.CharField(max_length=50)
    extension = models.CharField(max_length=10)
    sha1 = models.CharField(max_length=40)

    def download(self):
        return self.repository.getClient().getArtifact(self)

    def runtimeName(self):
        return "{}_{}_{}".format(self.groupid, self.artifactid, self.version)

    def getNewerVersions(self):
        artis = Artifact.objects.filter(groupid=self.groupid, artifactid=self.artifactid)
        newerVersions = []
        for a in artis:
            if StrictVersion(a.version) > StrictVersion(self.version):
                newerVersions.append(a)

        return newerVersions

    class Meta:
        ordering = ("groupid", "artifactid", "version")

class Deployment(models.Model):
    def __str__(self):
        return "{}:{}:{}".format(self.artifact.groupid, self.artifact.artifactid, self.artifact.version)

    applicationServer = models.ForeignKey(ApplicationServer, on_delete=models.DO_NOTHING)
    artifact = models.ForeignKey(Artifact, on_delete=models.DO_NOTHING)
    runtimeName = models.CharField(max_length=200, null=True)
    detected = models.DateTimeField(default=django.utils.timezone.now)

    def undeploy(self):
        return self.applicationServer.getClient().undeploy(self.runtimeName)


class Task(models.Model):

    NEW = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3
    ABORTED = 4

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    status = models.IntegerField(default=0)
    status_text = models.CharField(max_length=400)
    started = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.title

    def log(self, message):
        self.status_text = message
        TaskLog(message=message, task=self).save()
        return self

    def setStatus(self, status):
        self.status = status
        self.save()
        TaskLog(task=self, message="Status changed to {}".format(status)).save()
        return self

    def running(self):
        self.status = Task.RUNNING
        self.save()
        TaskLog(task=self, message="Status changed to Running").save()
        return self

    def complete(self):
        self.status = Task.COMPLETED
        self.save()
        TaskLog(task=self, message="Status changed to Complete").save()
        return self

    def failed(self):
        self.status = Task.FAILED
        self.save()
        TaskLog(task=self, message="Status changed to Failed").save()
        return self

    def aborted(self):
        self.status = Task.ABORTED
        self.save()
        TaskLog(task=self, message="Status changed to Aborted").save()
        return self


class TaskLog(models.Model):
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    message = models.CharField(max_length=200)
    task = models.ForeignKey(Task, models.DO_NOTHING)

