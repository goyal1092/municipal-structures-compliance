from django.contrib import admin
from .models import Organisation, Group
from django.db import models
from django_json_widget.widgets import JSONEditorWidget


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    