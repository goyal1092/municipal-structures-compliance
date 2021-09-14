from django.db import models
from django.conf import settings
from .user_methods import *


class MSCBase(models.Model):
    created = models.DateTimeField(auto_now_add=True,
                                   help_text="Date and time this object was created.")
    modified = models.DateTimeField(auto_now=True,
                                    help_text="Date and time this object was last modified.")

    class Meta:
        abstract = True


class Questionnaire(MSCBase):
    name = models.CharField(max_length=255)
    configuration = models.JSONField(default=dict, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    close = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name

    @property
    def response_count(self):
        return 0


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
    instruction = models.TextField(max_length=1024, blank=True, null=True)
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
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.section.label} -> {self.name}"


class QuestionLogic(MSCBase):
    action = models.CharField(max_length=32, choices=settings.LOGIC_ACTION)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    target = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="target")
    when = models.CharField(max_length=32, choices=settings.LOGIC_WHEN)
    values = models.CharField(max_length=255, null=True, blank=True)
