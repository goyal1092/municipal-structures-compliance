from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

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
        return self.response_set.count()

    @property
    def question_count(self):
        return Question.objects.filter(section__questionnaire=self).count()
    
    @property
    def question_response_percentage(self):
        return (self.response_count / self.question_count) * 100
    
    @property
    def overdue(self):
        return self.close < timezone.now()

    @property
    def is_submitted(self):
        return self.response_set.filter(is_submitted=True).exists()


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
    is_mandatory = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.section.label} -> {self.name}"

    def clean(self):
        input_type = self.input_type
        options = self.options
        default = settings.DEFAULT_INPUT_OPTIONS.get(input_type, None)

        if not input_type:
            raise ValidationError( "input type not found" )

        if "response_type" not in options:
            options["response_type"] = default["response_type"]

        if "validations" not in options:
            options["validations"] = default["validations"]

        for validation_type, validation in settings.QUESTION_BUILDER_VALIDATIONS.items():
            if input_type in validation["fields"]:
                if validation_type not in options:
                    raise ValidationError( f"{validation_type} are required for {input_type} question type. Example: {validation['example']}")
                elif options[validation_type] in [None, '', []]:
                    raise ValidationError( f"{validation['msg']}.Example: {validation['example']}")


class QuestionLogic(MSCBase):
    action = models.CharField(max_length=32, choices=settings.LOGIC_ACTION)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    when = models.CharField(max_length=32, choices=settings.LOGIC_WHEN)
    values = models.CharField(max_length=255, null=True, blank=True)
