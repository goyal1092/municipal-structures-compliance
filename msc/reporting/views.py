import io
import xlsxwriter
from collections import Counter

from django.shortcuts import render
from django.http import HttpResponse

from msc.questionnaire.models import Questionnaire
from msc.organisation.models import Organisation, Group
from msc.response.models import Response

from msc.questionnaire.utils import get_serialized_questioner
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import Http404

from msc.reporting.xls_reports import (
    create_province_report,
    create_national_report
)

def get_compiled_data(organisation, sections, questionnaire_id, survey_responses):
    compiled_data = []
    for section in sections:
        section_label = section["label"]
        section_questions = []
        for question in section["questions"]:
            responses = question["obj"].questionresponse_set.filter(
                response__in=survey_responses
            ).values(
                "response__organisation_id", "value"
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
                    "response__organisation_id", "value"
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
    return compiled_data


def download_report(request, questionnaire_id):
    user = request.user
    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)

    if request.method == 'POST':
        sections = get_serialized_questioner(questionnaire, user.organisation)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s_Report.xlsx' % f'{questionnaire.name}_{user.organisation.name}'

        if user.organisation.is_provincial:
            organisations = user.organisation.get_children(include_self=False)
            survey_responses = Response.objects.filter(
                questionnaire_id=questionnaire_id, organisation__in=organisations,
                is_submitted=True
            )

            submitted_orgs = survey_responses.values_list("organisation", flat=True).distinct()
            complied_yes = organisations.filter(id__in=submitted_orgs)
            complied_no = organisations.exclude(id__in=submitted_orgs)

            compiled_data = get_compiled_data(
                user.organisation, sections, questionnaire_id, survey_responses
            )
            xlsx_data = create_province_report(
                user.organisation, compiled_data, submitted_orgs, complied_yes, complied_no,
                organisations, questionnaire
            )
            response.write(xlsx_data)
            return response

        elif user.organisation.is_national:
            organisations = user.organisation.get_children(
                include_self=False
            ).order_by("name")

            total_data = []
            flat_sections_list = get_compiled_data(
                user.organisation, sections, questionnaire_id, []
            )

            for org in organisations:
                muni_organisations = org.get_children(include_self=False)
                survey_responses = Response.objects.filter(
                    questionnaire_id=questionnaire_id, organisation__parent=org,
                    is_submitted=True
                )
                compiled_data = get_compiled_data(
                    org, sections, questionnaire_id, survey_responses
                )

                for c in compiled_data:
                    for q in c["questions"]:
                        grouped_value = None
                        values = list(q["responses"].values())
                        if q["input_type"] == "number":
                            grouped_value = sum(values)
                        elif q["input_type"] in ["radio", "dropdown"]:
                            grouped_value = {i:values.count(i) for i in values}
                        elif q["input_type"] == "checkbox":
                            values = [item for sublist in values for item in sublist]
                            grouped_value = {i:values.count(i) for i in values}
                        q["grouped_value"] = grouped_value

                data = {
                    "label": org.name,
                    "id": org.id,
                    "responses": compiled_data,
                    "muni_organisations": muni_organisations,
                    "submitted": survey_responses,
                    "complied": survey_responses.count() == muni_organisations.count()
                }
                total_data.append(data)

            xlsx_data = create_national_report(
                user.organisation, total_data, questionnaire, flat_sections_list
            )
            response.write(xlsx_data)
            return response

    raise Http404
