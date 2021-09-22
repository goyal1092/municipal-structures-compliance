from django.contrib import admin
from .models import Response, QuestionResponse
from django.db import models
from django_json_widget.widgets import JSONEditorWidget


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_national:
            return qs

        if not request.user.organisation:
            return Response.objects.none()

        questionnaire_ids = Share.objects.filter(
            target_content_type__model="questionnaire",
            sharer_content_type__model="organisation",
            sharer_object_id=request.user.organisation.id
        ).values_list("target_object_id", flat=True)

        return qs.filter(questionnaire_id__in=questionnaire_ids)

@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_national:
            return qs

        if not request.user.organisation:
            return QuestionResponse.objects.none()

        questionnaire_ids = Share.objects.filter(
            target_content_type__model="questionnaire",
            sharer_content_type__model="organisation",
            sharer_object_id=request.user.organisation.id
        ).values_list("target_object_id", flat=True)

        return qs.filter(response__questionnaire_id__in=questionnaire_ids)
    