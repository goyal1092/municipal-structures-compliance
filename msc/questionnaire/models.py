from string import Template
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from ckeditor.fields import RichTextField
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .base import MSCBase

from msc.authentication.models import Share
from msc.organisation.models import Organisation


class Questionnaire(MSCBase):
    name = models.CharField(max_length=255)
    configuration = models.JSONField(default=dict, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    close = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)
    shareslist = GenericRelation(Share,
        content_type_field='target_content_type',
        object_id_field='target_object_id',
        related_query_name="questionnaire_shares")

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name

    @property
    def response_count(self):
        return self.response_set.count()

    @property
    def question_count(self):
        return Question.objects.filter(
            section__questionnaire=self, parent__isnull=True
        ).count()

    @property
    def question_response_percentage(self):
        if self.question_count == 0:
            return 0
        else:
            return (self.response_count / self.question_count) * 100

    @property
    def overdue(self):
        return self.close < timezone.now()

    def get_questions(self, include_child=False):
        q = {
            "section__questionnaire_id": self.id
        }
        if not include_child:
            q["parent__isnull"] = True

        return  Question.objects.filter(**q)

    def is_submitted(self, organisation):
        return self.response_set.filter(
            organisation=organisation,
            is_submitted=True
        ).exists()

    def question_response_count(self, organisation):
        response_count = 0

        response = self.response_set.filter(
            organisation=organisation
        ).first()
        if response:
            response_count = response.questionresponse_set.filter(
                question__parent__isnull=True
            ).count()

        return response_count

    def get_reminder_options(self, user):
        if not user.is_national and not user.is_provincial:
            return []

        children_ids = user.organisation.get_children(False).values_list(
            "id", flat=True
        )

        share_filters = {
            "target_content_type__model": "questionnaire",
            "sharer_content_type__model": "organisation",
            "target_object_id":self.id,
        }

        if user.is_provincial:
            share_filters["sharer_object_id__in"] = children_ids

        shares = Share.objects.filter(**share_filters)

        provinces = [share.sharer for share in shares.filter(relationship="admin")]
        municipalities = [share.sharer for share in shares.filter(relationship="viewer")]
        responses = self.response_set.filter(is_submitted=True).values_list(
            "organisation_id", flat=True
        )

        submited_munis = [muni for muni in municipalities if muni.id in responses]
        unsubmited_munis = [muni for muni in municipalities if muni.id not in responses]

        options = []
        if user.is_national and provinces:
            submited_provinces = []
            unsubmited_provinces = []

            org_type = provinces[0].org_type
            for province in provinces:
                munis = set(user.organisation.get_children(False))
                is_submitted = munis.issubset(set(submited_munis))
                if is_submitted:
                    submited_provinces.append(province)
                else:
                    unsubmited_provinces.append(province)

            for text in settings.EMAIL_ORG_USER_FILTER:
                if "unsubmitted" in text[0]:
                    filtered_organisation = unsubmited_provinces
                elif "submitted" in text[0]:
                    filtered_organisation = submited_provinces
                else:
                    filtered_organisation = provinces

                key = Template(text[0]).substitute({'org_type': org_type})
                count = len(filtered_organisation)
                options.append({
                    "name": key,
                    "text": Template(text[1]).substitute({'org_type': org_type, 'count': count}),
                    "organisations": filtered_organisation,
                    "count": count,
                })
        if municipalities:
            org_type = municipalities[0].org_type
            for text in settings.EMAIL_ORG_USER_FILTER:
                if "unsubmitted" in text[0]:
                    filtered_organisation = unsubmited_munis
                elif "submitted" in text[0]:
                    filtered_organisation = submited_munis
                else:
                    filtered_organisation = municipalities

                key = Template(text[0]).substitute({'org_type': org_type})
                count = len(filtered_organisation)
                options.append({
                    "name": key,
                    "text": Template(text[1]).substitute({'org_type': org_type, 'count': count}),
                    "organisations": filtered_organisation,
                    "count": count,
                })

        return options

@receiver(pre_delete, sender=Questionnaire, dispatch_uid='questionnaire_delete_signal')
def delete_linked_shares(sender, instance, using, **kwargs):
    instance.shareslist.all().delete()

class Section(MSCBase):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    label = models.CharField(max_length=1024)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.questionnaire.name} -> {self.label}"


class Question(MSCBase):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    #instruction = models.TextField(max_length=1024, blank=True, null=True)
    instruction = RichTextField(blank=True, null=True, help_text="Add links, formatting etc. to help guide the question")

    input_type = models.CharField(
        max_length=32, choices=settings.QUESTION_INPUT_TYPES,
        db_index=True
    )
    name = models.CharField(
        max_length=512, blank=True, null=True,
        db_index=True
    )
    text = models.TextField(blank=True, null=True)
    options = models.JSONField(default=dict, null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True)
    is_mandatory = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.section.label} -> {self.name}"

    @property
    def get_key(self):
        return f'{self.section_id}_{self.id}'

    def get_child_questions(self):
        return Question.objects.filter(
            parent=self
        )

    def get_summary_results(self, responses):

        qr_responses = []
        for response in responses:
            qr_response = response.questionresponse_set.filter(
                question=self
            ).first()

            if qr_response:
                if self.input_type != "checkbox":
                    qr_responses.append(qr_response.value)
                else:
                    qr_responses = qr_responses + qr_response.value

        max_data = {}
        if qr_responses:
            max_choice = max(qr_responses, key = qr_responses.count)
            max_data =  {
                "choice":max_choice,
                "count":qr_responses.count(max_choice),
            }

        all_choices = {}
        for choice in self.options.get("choices", []):
            all_choices[choice] = qr_responses.count(choice)

        return {
            "total_response_count": len(responses),
            "max": max_data,
            "all": all_choices
        }



class QuestionLogic(MSCBase):
    action = models.CharField(max_length=32, choices=settings.LOGIC_ACTION)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    when = models.CharField(max_length=32, choices=settings.LOGIC_WHEN)
    values = models.CharField(max_length=255, null=True, blank=True)
