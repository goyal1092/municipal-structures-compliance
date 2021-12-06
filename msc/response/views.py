from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Response, QuestionResponse
from .utils import validate_question_response

from msc.organisation.models import Organisation
from msc.questionnaire.models import Questionnaire, Question


def submit_form(questionnaire, response):
    errors = {}
    questions = questionnaire.get_questions(False)
    responses = response.questionresponse_set.filter(is_valid=True)

    for question in questions:
        response = responses.filter(question=question).first()
        if question.is_mandatory and not response:
            errors[question.id] = "This question is mandatory"
            continue

        child_questions = question.get_child_questions()
        for child in child_questions:
            logic = child.questionlogic_set.first()
            if logic:
                child_qr = responses.filter(question=child).exists()
                if logic.when == "parent_value" and logic.values == response.value and not child_qr:
                    errors[child.id] = "This question is mandatory"
                elif logic.when == "parent" and not child_qr:
                    errors[child.id] = "This question is mandatory"
    return  errors

def get_response_val(request, question_key, input_type):
    val = None
    if input_type == "checkbox":
        val = request.POST.getlist(question_key, None)
    else:
        val = request.POST.get(question_key, None)
        if val:
            val = val.strip()

    return val

def save_response(request, questionnaire, response_obj):
    user = request.user
    validation_errors = {}

    questions = questionnaire.get_questions()

    for question in questions:
        # question key
        question_key = question.get_key
        child_questions = question.get_child_questions()

        val = get_response_val(request, question_key, question.input_type)
        if not val:
            # Delete Responses linked to this question
            question_ids = list(
                child_questions.values_list("id", flat=True)
            ) + [question.id]
            QuestionResponse.objects.filter(
                response=response_obj,
                question_id__in=question_ids
            ).delete()
            continue

        # Validate question response
        is_valid, msg, value = validate_question_response(
            question, val
        )

        if not is_valid:
            validation_errors[question_key] = msg
            continue

        qr_response = QuestionResponse.objects.filter(
            response=response_obj, question=question
        ).first()

        if not qr_response:
            qr_response = QuestionResponse.objects.create(
                respondent=user,
                response=response_obj,
                question=question,
                value=value,
                is_valid=is_valid
            )
        else:
            qr_response.user = user
            version = qr_response.version + 1
            qr_response.version = version
            qr_response.value = value
            qr_response.is_valid = is_valid
            qr_response.save()


        for child in child_questions:
            child_qr = QuestionResponse.objects.filter(
                response=response_obj, question=child
            ).first()

            logics = child.questionlogic_set.all()
            for logic in logics:
                val = get_response_val(request, child.get_key, child.input_type)

                is_logic_valid = False
                if val:
                    if isinstance(qr_response.value, list):
                        is_logic_valid = logic.values in qr_response.value
                    else:
                        is_logic_valid = logic.values == qr_response.value


                if is_logic_valid:
                    is_valid, msg, value = validate_question_response(
                        child, val
                    )
                    if not is_valid:
                        validation_errors[child.get_key] = msg
                        continue

                    if child_qr:
                        child_qr.user = user
                        version = child_qr.version + 1
                        child_qr.version = version
                        child_qr.value = value
                        child_qr.is_valid = is_valid
                        child_qr.save()

                    else:
                        child_qr = QuestionResponse.objects.create(
                            respondent=user,
                            response=response_obj,
                            question=child,
                            value=value,
                            is_valid=is_valid
                        )

                else:
                    QuestionResponse.objects.filter(
                        response=response_obj, question=child
                    ).delete()


    return validation_errors
