import io
import xlsxwriter

from django.shortcuts import render
from django.http import HttpResponse

from msc.questionnaire.models import Questionnaire
from msc.organisation.models import Organisation, Group
from msc.response.models import Response

from .province import Cover, AllData, ComplianceOverview, CompliedYes, CompliedNo, ResultSummary, QuestionBreakdown
from msc.questionnaire.utils import get_serialized_questioner
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import Http404

def create_excel(
        province, compiled_data, submitted_orgs, complied_yes, complied_no,
        all_orgs, questionnaire
    ):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    org_name = province.name

    # Cover Page
    cover = Cover()
    cover_page = cover.create_sheet(workbook, 'Cover Page')
    cover.format(workbook, cover_page)

    # All Data Tab
    all_data = AllData()
    all_data_page = all_data.create_sheet(workbook, 'Copy of All Data')

    all_data.format(workbook, all_data_page, compiled_data, list(list(complied_yes)+list(complied_no)))
    cover.add_link(workbook, cover_page, 6, 0, "Copy of All Data")

    # Compliance Overview Tab
    overview = ComplianceOverview()
    overview_page = overview.create_sheet(workbook, 'Compliance Overview')
    overview.format(
        workbook, overview_page, org_name, all_orgs, questionnaire
    )
    cover.add_link(workbook, cover_page, 7, 0, "Compliance Overview")

    # Complied yes Tab
    compliedyes = CompliedYes()
    complied_yes_page = compliedyes.create_sheet(workbook, 'Complied - Yes')
    compliedyes.format(
        workbook, complied_yes_page, org_name, complied_yes
    )
    cover.add_link(workbook, cover_page, 8, 0, "Complied - Yes")

    # Complied No Tab
    compliedno = CompliedNo()
    complied_no_page = compliedno.create_sheet(workbook, 'Complied - No')
    compliedno.format(
        workbook, complied_no_page, org_name, complied_no
    )
    cover.add_link(workbook, cover_page, 9, 0, "Complied - No")

    # Result Summary Tab
    result_summary = ResultSummary()
    result_summary_page = result_summary.create_sheet(workbook, 'Provincial Form Result Summary')
    result_summary.format(
        workbook, result_summary_page, org_name, complied_yes, compiled_data
    )
    cover.add_link(workbook, cover_page, 10, 0, "Provincial Form Result Summary")

    questions = []
    for section in compiled_data:
        questions = questions + section["questions"]

    for question in questions:
        if question["input_type"] not in result_summary.excluded_question_types:
            question_breakdown = QuestionBreakdown()
            question_breakdown_page = question_breakdown.create_sheet(
                workbook, f'Breakdown of Question {question["sno"]}'
            )
            question_breakdown.format(
                workbook, question_breakdown_page, org_name, all_orgs, question
            )
    if questions:
        cover.add_link(workbook, cover_page, 11, 0, f'Breakdown of Question {questions[0]["sno"]}')

    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data


def download_report(request, questionnaire_id):
    user = request.user
    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)

    if not user.organisation.is_provincial:
        raise Http404
    
    if request.method == 'POST':
        sections = get_serialized_questioner(questionnaire, user.organisation)
        organisations = user.organisation.get_children(include_self=False)
        survey_responses = Response.objects.filter(
            questionnaire_id=questionnaire_id, organisation__in=organisations,
            is_submitted=True
        )

        submitted_orgs = survey_responses.values_list("organisation", flat=True).distinct()
        complied_yes = organisations.filter(id__in=submitted_orgs)
        complied_no = organisations.exclude(id__in=submitted_orgs)

        compiled_data = []
        for section in sections:
            section_label = section["label"]
            section_questions = []
            for question in section["questions"]:

                responses = question["obj"].questionresponse_set.filter(
                    response__in=survey_responses
                ).values(
                    "response__organisation__id", "value"
                )

                responses = {x["response__organisation_id"]: x["value"] for x in responses}

                section_questions.append({
                    "label": f'{question["sno"]} - {question["obj"].input_type}',
                    "text": question["obj"].text,
                    "responses": responses,
                    "id": question["obj"].id,
                    "sno": question["sno"],
                    "input_type": question["obj"].input_type,
                    "obj": question["obj"]
                })
                for child in question["children"]:

                    responses = child["obj"].questionresponse_set.filter(
                        response__in=survey_responses
                    ).values(
                        "response__organisation__id", "value"
                    )

                    responses = {x["response__organisation_id"]: x["value"] for x in responses}
                    section_questions.append({
                        "label": f'{child["sno"]} - {child["obj"].input_type}',
                        "text": child["obj"].text,
                        "responses": responses,
                        "id": child["obj"].id,
                        "sno": child["sno"],
                        "input_type": child["obj"].input_type,
                        "obj": child["obj"]
                    })

            compiled_data.append({
                "label": section_label,
                "questions": section_questions
            })


        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s_Report.xlsx' % f'{questionnaire.name}_{user.organisation.name}'


        xlsx_data = create_excel(
            user.organisation, compiled_data, submitted_orgs, complied_yes, complied_no,
            organisations, questionnaire
        )
        response.write(xlsx_data)
        return response

    raise Http404
