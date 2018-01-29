# coding=utf-8
from django.contrib import admin, auth
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name="overview"),
    path('deploy', views.DeployView.as_view(), name="deploy"),
    path("as/<int:appServ>", views.AppServer.as_view(), name="appServ")
]
