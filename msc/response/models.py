from django.db import models
from django.conf import settings
from msc.questionnaire.models import MSCBase
from .utils import ValidateQuestionResponse



class Response(MSCBase):
    questionnaire = models.ForeignKey("questionnaire.Questionnaire", on_delete=models.CASCADE)
    organisation = models.ForeignKey("organisation.Organisation", on_delete=models.CASCADE)
    configuration = models.JSONField(default=dict, blank=True, null=True)
    is_submitted = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.organisation} -> {self.questionnaire.name}"


class QuestionResponse(MSCBase):
    response = models.ForeignKey("Response", on_delete=models.CASCADE)
    respondent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey("questionnaire.Question", on_delete=models.CASCADE)
    value = models.JSONField(default=dict, blank=True, null=True)
    is_valid = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("respondent", "question", "version",)


    def __str__(self):
        return f"{self.respondent.email} -> {self.response.organisation} -> {self.question.name}"

    def validate(self):
        validation = ValidateQuestionResponse()
        return validation.run_validation(self.question, self.value)