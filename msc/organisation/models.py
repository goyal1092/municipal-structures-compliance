from django.db import models
from msc.questionnaire.models import MSCBase


class Group(MSCBase):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Organisation(MSCBase):
    name = models.CharField(max_length=256)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    org_type = models.ForeignKey("Group", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_children(self, include_self=True):
        org_ids = []
        if include_self:
            org_ids.append(self.id)

        org_ids = org_ids + list(
            Organisation.objects.filter(parent=self).values_list("id", flat=True)
        )
        return Organisation.objects.filter(id__in=org_ids)

    @property
    def is_national(self):
        return self.parent == None

    @property
    def is_provincial(self):
        return self.parent and self.parent.parent == None