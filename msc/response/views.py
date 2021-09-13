from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Response, QuestionResponse
from msc.organisation.models import Organisation
from msc.questionnaire.models import Questionnaire, Question
from msc.questionnaire.utils import get_serialized_questioner


def save_question_response(
        value, question, user, response
    ):
    qr_response = question["response"]
    version = 0
    response_val = ""
    if qr_response:
        version = qr_response.version
        response_val = qr_response.value

    version += 1
    qr_response = QuestionResponse(
        respondent=user,
        response=response,
        question_id=question["obj"].id,
        value=value,
        version=version,
    )

    validation = qr_response.validate()
    qr_response.is_valid = validation["is_valid"]
    qr_response.value = validation["response"]

    save_response = True

    if version == 1 and not validation["response"]:
        save_response = False
    if version > 1 and (response_val == qr_response.value):
        save_response = False

    if save_response:
        qr_response.save()

    return validation["is_valid"],  validation["msg"]

def submit_form(questionnaire, response):
    errors = {}
    responses = response.questionresponse_set.filter(is_valid=True)
    questions = Question.objects.filter(section__questionnaire=questionnaire)
    for question in questions:
        question_response = responses.filter(
            question=question.id
        ).order_by("-version").first()
        if (
            (not question_response and question.is_mandatory) or
            (question_response and not question_response.value)
        ):
            errors[question.id] = "This question is mandatory"

        
        if question.id not in errors:
            for logic in question.questionlogic_set.all():
                if logic.action == "make_required" and "parent" in logic.when:
                    parent = question.parent
                    parent_question_resposne = responses.filter(
                        question=parent.id
                    ).order_by("-version").first()

                    if (
                        ((logic.when == "parent" and parent_question_resposne) and
                        (not question_response or not question_response.value)) or
                        ((logic.when == "parent_value" and parent_question_resposne.value == logic.values) and
                        (not question_response or not question_response.value))
                    ):
                        errors[question.id] = "This question is mandatory"

    return errors


def save_response(request, organisation, questionnaire, response_obj):
    user = request.user
    validation_errors = {}
    sections = get_serialized_questioner(questionnaire, organisation)

    for section in sections:
        for ques in section["questions"]:
            val = ""
            if ques["obj"].input_type == "checkbox":
                val = request.POST.getlist(ques["sno"], [])
            else:
                val = request.POST.get(ques["sno"], "")

            is_valid, msg = save_question_response(val, ques, user, response_obj)

            if not is_valid:
                validation_errors[ques["sno"]] = msg

            if ques["children"]:
                for child in ques["children"]:
                    val = ""
                    if child["obj"].input_type == "checkbox":
                        val = request.POST.getlist(child["sno"], "")
                    else:
                        val = request.POST.get(child["sno"], "")
                    is_valid, msg = save_question_response(val, child, user, response_obj)
                    if not is_valid:
                        validation_errors[ques["sno"]] = msg
    return validation_errors
