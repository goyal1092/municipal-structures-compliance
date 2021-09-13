from django.contrib import admin
from .models import Response, QuestionResponse
from django.db import models
from django_json_widget.widgets import JSONEditorWidget


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    