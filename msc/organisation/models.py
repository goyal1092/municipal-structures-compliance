from django.db import models
from django.conf import settings
from msc.questionnaire.models import MSCBase


class Group(MSCBase):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Organisation(MSCBase):
    name = models.CharField(max_length=256)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    org_type = models.ForeignKey("Group", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name