import io
import xlsxwriter

from .cover import Cover
from .all_data import AllData
from .compliance_overview import ComplianceOverview
from .complied_yes import CompliedYes
from .complied_no import CompliedNo
from .result_summary import ResultSummary
from .question_breakdown import QuestionBreakdown

def create_excel(organisation, total_data, questionnaire, sections):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    org_name = "National"

    # Cover Page
    cover = Cover()
    cover_page = cover.create_sheet(workbook, 'Cover Page')
    cover.format(workbook, cover_page)

    # # All Data Tab
    all_data = AllData()
    all_data_page = all_data.create_sheet(workbook, 'Copy of All Data')

    all_data.format(workbook, all_data_page, total_data, sections)
    cover.add_link(workbook, cover_page, 6, 0, "Copy of All Data")

    # Compliance Overview Tab
    overview = ComplianceOverview()
    overview_page = overview.create_sheet(workbook, 'Compliance Overview')
    overview.format(
        workbook, overview_page, org_name, total_data
    )
    cover.add_link(workbook, cover_page, 7, 0, "Compliance Overview")

    # Complied yes Tab
    compliedyes = CompliedYes()
    complied_yes_page = compliedyes.create_sheet(workbook, 'Complied - Yes')
    compliedyes.format(
        workbook, complied_yes_page, org_name, total_data
    )
    cover.add_link(workbook, cover_page, 8, 0, "Complied - Yes")

    # Complied No Tab
    compliedno = CompliedNo()
    complied_no_page = compliedno.create_sheet(workbook, 'Complied - No')
    compliedno.format(
        workbook, complied_no_page, org_name, total_data
    )
    cover.add_link(workbook, cover_page, 9, 0, "Complied - No")
    #
    # Result Summary Tab
    result_summary = ResultSummary()
    result_summary_page = result_summary.create_sheet(
        workbook, 'National Form Result Summary'
    )
    result_summary.format(
        workbook, result_summary_page, org_name, total_data, sections
    )
    cover.add_link(workbook, cover_page, 10, 0, "National Form Result Summary")
    #
    questions = []
    for section in sections:
        questions = questions + section["questions"]

    for question in questions:
        if question["input_type"] not in result_summary.excluded_question_types:
            question_breakdown = QuestionBreakdown()
            question_breakdown_page = question_breakdown.create_sheet(
                workbook, f'Breakdown of Question {question["sno"]}'
            )
            question_breakdown.format(
                workbook, question_breakdown_page, org_name, total_data, question
            )
    if questions:
        cover.add_link(workbook, cover_page, 11, 0, f'Breakdown of Question {questions[0]["sno"]}')

    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data
