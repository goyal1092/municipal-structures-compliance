from django.contrib import admin
from django.db import models
from .models import Questionnaire, Question, Section, QuestionLogic
from django_json_widget.widgets import JSONEditorWidget
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from msc.authentication.models import Share
from .widgets import SharesWidget, ArrayWidget
from msc.organisation.models import Organisation
from django.contrib.admin import SimpleListFilter

from django import forms

class QuestionnaireForm(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = '__all__'

    shares = forms.CharField(required=False, label="")

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
    list_display = ("name", "start", "close", "is_published",)
    list_filter = ('is_published', "start", "close")
    search_fields = ("name",)

    fieldsets = (
        (None, {'fields': ('name',)}),
        ("Configurations", {'fields': (('start', 'close',), "is_published",)}),
        ('Shares', {'fields': ('shares',)}),
    )
    form = QuestionnaireForm
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def get_readonly_fields(self, request, obj=None):
        if obj and request.user.is_admin:
            return self.readonly_fields + ('name', 'start', 'close', 'is_published',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        user = request.user
        org_content_type = ContentType.objects.get_for_model(
            Organisation
        )
        ques_content_type = ContentType.objects.get_for_model(
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
                target_content_type=ques_content_type,
                target_object_id=obj.id,
                sharer_content_type=org_content_type,
                sharer_object_id=creator_org,
                shared_by=request.user,
                relationship="creator"
            )

        shares = [int(idx) for idx in request.POST.getlist("shares", [])]
        shared_with = Share.objects.filter(
            target_content_type=ques_content_type,
            target_object_id=obj.id,
            sharer_content_type=org_content_type,
        )

        if shared_with:
            shared_with = [share.sharer.id for share in shared_with if share.sharer]

        if request.user.is_superuser or not request.user.is_national:
            organisations = Organisation.objects.filter(
                org_type_id__in=shares
            ).exclude(
                id__in=shared_with
            )

            for org in organisations:
                relationship = "viewer"

                if org.is_national:
                    relationship = "creator"
                elif org.is_provincial:
                    relationship = "admin"
                Share.objects.create(
                    target_content_type=ques_content_type,
                    target_object_id=obj.id,
                    sharer_content_type=org_content_type,
                    sharer_object_id=org.id,
                    shared_by=request.user,
                    relationship=relationship
                )

        else:
            organisations = Organisation.objects.filter(
                id__in=shares
            ).exclude(
                id__in=shared_with
            )

            for org in organisations:
                relationship = "viewer"
                if org.is_national:
                    relationship = "creator"
                elif org.is_provincial:
                    relationship = "admin"
                Share.objects.create(
                    target_content_type=ques_content_type,
                    target_object_id=obj.id,
                    sharer_content_type=org_content_type,
                    sharer_object_id=org.id,
                    shared_by=request.user,
                    relationship=relationship
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


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

    choices = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['choices'].widget = ArrayWidget(
                instance=self.instance
            )
        else:
            self.fields['choices'].widget = ArrayWidget(
                instance=None
            )

class QuestionnaireFilter(SimpleListFilter):
    title = 'Questionnaire name' # or use _('country') for translated title
    parameter_name = 'questionnaire'

    def lookups(self, request, model_admin):
        questionnaires = Questionnaire.objects.all()
        return [(q.id, q.name) for q in questionnaires]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(section__questionnaire_id=self.value())
        return queryset

class IsChildFilter(SimpleListFilter):
    title = 'Is child question'
    parameter_name = 'child'

    def lookups(self, request, model_admin):
        return [(q, q) for q in ["yes", "no"]]

    def queryset(self, request, queryset):
        if self.value():
            is_child = self.value() != "yes"
            return queryset.filter(parent__isnull=is_child)
        return queryset


@admin.register(Question)
class Question(admin.ModelAdmin):
    form = QuestionForm
    fieldsets = (
        (None, {'fields': ('name', 'text', 'instruction', 'section',)}),
        ("Configurations", {'fields': ('input_type', 'order', 'is_mandatory', 'parent', 'choices',)}),
    )
    list_filter = ['section', 'input_type', QuestionnaireFilter, IsChildFilter]
    inlines = [QuestionLogicInline,]
    search_fields = ("text", "input_type", "name", "section__label",)
    list_display = ("text", "name", "input_type", "order",)

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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        user = request.user
        if obj.input_type in ["radio", "dropdown", "checkbox"]:
            choices = request.POST.getlist("choices", [])
            options = obj.options
            options["choices"] = choices
            obj.options = options
            obj.save()


class QuestionnaireFilter(SimpleListFilter):
    title = 'Questionnaire name' # or use _('country') for translated title
    parameter_name = 'questionnaire'

    def lookups(self, request, model_admin):
        questionnaires = Questionnaire.objects.all()
        return [(q.id, q.name) for q in questionnaires]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(questionnaire__id=self.value())
        return queryset

class PublishedQuestionnaireFilter(SimpleListFilter):
    title = 'Published Questionnaire' # or use _('country') for translated title
    parameter_name = 'published'

    def lookups(self, request, model_admin):
        return [(q, q) for q in ["yes", "no"]]

    def queryset(self, request, queryset):
        if self.value():
            show = self.value() == "yes"
            return queryset.filter(questionnaire__is_published=show)
        return queryset


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("questionnaire", "label", "order", "get_questions_count")
    list_filter = [QuestionnaireFilter, PublishedQuestionnaireFilter]
    fields = ('questionnaire', 'label', 'order','get_questions_count', 'get_question_links', )
    readonly_fields = ('get_questions_count', 'get_question_links')
    search_fields = ("label", "questionnaire__name",)

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
            return f"<a href='{url}'>{display_name}</a></br>"

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
