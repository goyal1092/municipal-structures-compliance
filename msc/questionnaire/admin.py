from django.contrib import admin
from django.db import models
from .models import Questionnaire, Question, Section, QuestionLogic
from django_json_widget.widgets import JSONEditorWidget
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ("name", "start", "close")
    fields = ('name', 'start', 'close', 'is_published', 'configuration', )
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }


class QuestionLogicInline(admin.StackedInline):
    model = QuestionLogic
    fk_name="question"
    extra=0

@admin.register(Question)
class Question(admin.ModelAdmin):
    model = Question
    fields = (
        'section', 'input_type', 'name', 'text',
        'instruction', 'parent', 'order', 'options',
        'is_mandatory'
    )
    list_filter = ['section__label', 'input_type']
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    inlines = [QuestionLogicInline,]

    def get_changeform_initial_data(self, request):
        input_type = request.GET.get("input_type", None)
        defaults = super().get_changeform_initial_data(request)
        if input_type:
            options = settings.DEFAULT_INPUT_OPTIONS.get(input_type, "")
            defaults['options'] = options
        return defaults
    

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("questionnaire", "label")
    list_filter = ['questionnaire__name',]
    fields = ('questionnaire', 'label', 'order','get_questions_count', 'get_question_links', )
    readonly_fields = ('get_questions_count', 'get_question_links')


    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['question_types'] = settings.QUESTION_INPUT_TYPES
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def get_questions_count(self, instance):
        if instance:
            return instance.question_set.count()
        return "-"

    get_questions_count.short_description = "Total number of Questions"
    get_questions_count.allow_tags = True

    def get_question_links(self, instance):
        def get_link(obj):
            display_name = f"{obj.name} -> {obj.input_type}"
            url = reverse("admin:questionnaire_question_change", args=[obj.id])
            return f"<a href='{url}'>{display_name}</a>"

        if instance.id:
            questions = instance.question_set.all()
            if not questions:
                return "-"
            return mark_safe(
                ", ".join([get_link(question) for question in questions])
            )
        else:
            return "-"

    get_question_links.short_description = "Questions"
    get_question_links.allow_tags = True
