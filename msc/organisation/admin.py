from django.contrib import admin
from .models import Organisation, Group, EmailActivity
from django.db import models
from django_json_widget.widgets import JSONEditorWidget


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'org_type',)
    list_filter = ('org_type', 'parent')
    search_fields = ('name',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass

@admin.register(EmailActivity)
class EmailActivityAdmin(admin.ModelAdmin):
    pass
