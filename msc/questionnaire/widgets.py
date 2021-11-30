import json

from django.forms.widgets import Widget
from django.contrib import admin
from django import forms
from django.db.models import Count

from msc.authentication.models import Share
from msc.organisation.models import Organisation



class ArrayWidget(Widget):
    template_name = 'widgets/array_widget.html'

    def __init__(self, attrs=None, instance=None, current_user=None):
        self.instance = instance
        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs=None, instance=None):

        instance = self.instance
        choices = []
        show = False
        if instance:
            choices = instance.options.get("choices", [])
            if instance.input_type in ["dropdown", "checkbox", "radio"]:
                show = True

        context = {
            "show": show,
            "choices": choices
        }

        return context


class SharesWidget(Widget):
    template_name = 'widgets/share.html'

    def __init__(self, attrs=None, instance=None, current_user=None):
        self.instance = instance
        self.current_user = current_user
        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs=None, instance=None):

        instance = self.instance
        current_user = self.current_user
        context = super().get_context(name, value, attrs)

        if current_user.is_superuser:
            organisations = Organisation.objects.all()
        else:
            organisations = current_user.organisation.get_children(include_self=False)

        shares = None

        if instance:
            shares = Share.objects.filter(
                target_content_type__model="questionnaire",
                target_object_id=instance.id,
                sharer_content_type__model="organisation"
            )

        selected_org = current_user.organisation
        if instance and shares:
            creator = shares.filter(relationship="creator").first()
            if creator:
                selected_org = creator.sharer
            else:
                selected_org = None

        organisation_types = list(
            organisations.values(
                "org_type", "org_type__name", "org_type__id"
            ).annotate(count=Count('org_type'))
        )

        org_types = []

        for org_type in organisation_types:
            shared_with = 0
            if instance:
                org_ids = organisations.filter(org_type_id=org_type["org_type__id"]).values_list("id", flat=True)
                shared_with = shares.filter(sharer_object_id__in=org_ids).count()
            org_type["shared_with"] = shared_with

        context.update({
            "obj": instance,
            "current_user": current_user,
            "organisations": organisations,
            "selected_org": selected_org,
            "organisation_types": organisation_types,
        })

        if current_user.is_national:
            context["has_shares_with"] = [share.sharer for share in shares]
        return context
