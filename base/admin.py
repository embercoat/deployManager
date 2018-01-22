from django.contrib import admin

# Register your models here.
from base.models import *

admin.site.register(Repository)
admin.site.register(ApplicationServer)
admin.site.register(Artifact)
admin.site.register(Deployment)