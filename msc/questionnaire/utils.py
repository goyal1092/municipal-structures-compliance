import string
from .models import Questionnaire
from msc.response.models import Response


def serialize_question(
        question, section_no,
        question_no, response, is_child=False
    ):
    if is_child:
        question_no = string.ascii_lowercase[question_no]

    sno = f"{section_no}.{question_no}"
    return {
        "sno": sno,
        "template": f"question/{question.input_type}.html",
        "obj": question,
        "response": serialize_response(question, response)
    }

def serialize_response(question, response):
    if response:
        question_response = response.questionresponse_set.filter(
            question=question).order_by("-version").first()
        if question_response:
            return question_response

    return None

def get_serialized_questioner(questionnaire, organisation):
    data = []
    sections = questionnaire.section_set.all()
    response = Response.objects.filter(
        questionnaire=questionnaire, organisation=organisation
    ).first()

    for idx, section in enumerate(sections):
        subdata = {}
        section_no = idx + 1
        questions = section.question_set.filter(parent__isnull=True)

        serialized_quesions = []
        for qidx, question in enumerate(questions):
            question_no = qidx + 1
            ques_details = serialize_question(question, section_no, question_no, response)

            child_questions = []
            for cidx, child in enumerate(list(section.question_set.filter(parent=question))):
                child_questions.append(serialize_question(child, ques_details["sno"], cidx, response, True))

            ques_details["children"] = child_questions
            serialized_quesions.append(ques_details)

        data.append({
            "label": f"Section - {idx+1} {section.label}",
            "questions": serialized_quesions
        })

    return data