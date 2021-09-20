from django.contrib import admin
from django.db import models
from .models import Questionnaire, Question, Section, QuestionLogic
from django_json_widget.widgets import JSONEditorWidget
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from msc.authentication.models import Share
from .widgets import SharesWidget
from msc.organisation.models import Organisation

from django import forms

class QuestionnaireForm(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = '__all__'

    shares = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['shares'].widget = SharesWidget(
                instance=self.instance, current_user=self.current_user
            )
        else:
            self.fields['shares'].widget = SharesWidget(
                instance=None, current_user=self.current_user
            )

@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ("name", "start", "close")
    fields = ('name', 'start', 'close', 'is_published', 'configuration', 'shares',)
    form = QuestionnaireForm
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        user = request.user
        org_type = ContentType.objects.get_for_model(
            Organisation
        )
        ques_type = ContentType.objects.get_for_model(
            Questionnaire
        )

        if not change:
            creator_org = user.organisation_id
            if user.is_superuser:
                try:
                    creator_org = int(request.POST["creator"])
                except:
                    pass

            if not creator_org:
                creator_org = Organisation.objects.filter(parent__isnull=True).first().id

            # creator share
            Share.objects.create(
                target_content_type=ques_type,
                target_object_id=obj.id,
                sharer_content_type=org_type,
                sharer_object_id=creator_org,
                shared_by=request.user,
                relationship="creator"
            )

        shares = [int(idx) for idx in request.POST.getlist("shares", [])]
        shared_with = Share.objects.filter(
                target_content_type=ques_type,
                target_object_id=obj.id,
                sharer_content_type=org_type,
            )

        if shared_with:
            shared_with = [share.sharer.id for share in shared_with]

        if request.user.is_superuser:
            organisations = Organisation.objects.filter(
                org_type_id__in=shares
            ).exclude(
                id__in=shared_with
            ).values_list("id", flat=True)

            for org in organisations:
                Share.objects.create(
                    target_content_type=ques_type,
                    target_object_id=obj.id,
                    sharer_content_type=org_type,
                    sharer_object_id=org,
                    shared_by=request.user,
                    relationship="viewer"
                )

        elif request.user.is_national:
            organisations = Organisation.objects.filter(
                id__in=shares
            ).exclude(
                id__in=shared_with
            ).values_list("id", flat=True)

            for org in organisations:
                Share.objects.create(
                    target_content_type=ques_type,
                    target_object_id=obj.id,
                    sharer_content_type=org_type,
                    sharer_object_id=org,
                    shared_by=request.user,
                    relationship="viewer"
                )
            

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        if not request.user.organisation:
            return Questionnaire.objects.none()

        questionnaire_ids = Share.objects.filter(
            target_content_type__model="questionnaire",
            sharer_content_type__model="organisation",
            sharer_object_id=request.user.organisation.id
        ).values_list("target_object_id", flat=True)

        return qs.filter(id__in=questionnaire_ids)

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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        if not request.user.organisation:
            return Question.objects.none()

        questionnaire_ids = Share.objects.filter(
            target_content_type__model="questionnaire",
            sharer_content_type__model="organisation",
            sharer_object_id=request.user.organisation.id
        ).values_list("target_object_id", flat=True)

        return qs.filter(section__questionnaire_id__in=questionnaire_ids)
    

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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        if not request.user.organisation:
            return Question.objects.none()

        questionnaire_ids = Share.objects.filter(
            target_content_type__model="questionnaire",
            sharer_content_type__model="organisation",
            sharer_object_id=request.user.organisation.id
        ).values_list("target_object_id", flat=True)

        return qs.filter(questionnaire_id__in=questionnaire_ids)


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
