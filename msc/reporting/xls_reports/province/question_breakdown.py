
from ..base import ReportingBase

class QuestionBreakdown(ReportingBase):

    def render_subheading(self, workbook, worksheet, heading):
        heading_cell_format = workbook.add_format({
            'bold': True,
            'font_name': self.font_name,
            'font_size': 16,
        })
        heading_cell_format.set_text_wrap()
        heading_cell_format.set_align('vcenter')
        worksheet.write(
            2, 0, heading, heading_cell_format
        )

    def render_question_options(self, workbook, worksheet, question):
        heading_cell_format = workbook.add_format({
            'bold': True,
            'font_name': self.font_name,
            'font_size': 16,
        })
        heading_cell_format.set_text_wrap()
        heading_cell_format.set_align('vcenter')
        worksheet.write(
            3, 0, f'Options : {", ".join(question.options["choices"])}', heading_cell_format
        )

    def render_response_table(self, workbook, worksheet, orgs, question):
        heading_cell_format = workbook.add_format({
            'bold': True, 'font_size': 14,
            'font_name': self.font_name,
            'border': 1
        })
        heading_cell_format.set_text_wrap()
        heading_cell_format.set_align('center')
        heading_cell_format.set_align('vcenter')
        heading_cell_format.set_bg_color('#C5C5C5')

        row = 6
        col = 0
        worksheet.write(
            row,  col, 'Name of organisation',
            heading_cell_format
        )

        worksheet.write(
            row,  col+1, 'Response',
            heading_cell_format
        )

        cell_format = workbook.add_format({
            'bold': True, 'font_size': 14,
            'font_name': self.font_name,
            'border': 1
        })
        cell_format.set_text_wrap()
        cell_format.set_align('center')
        cell_format.set_align('vcenter')

        for org in orgs:
            response = question["responses"].get(org.id, "-")
            row = row + 1
            worksheet.write(
                row,  col,
                org.name, cell_format
            )
            if isinstance(response, list):
                response = ",".join(response)
            worksheet.write(
                row,  col+1,
                response, cell_format
            )

    def format(self, workbook, worksheet, org_name, all_orgs, question):
        self.logo(
            workbook, worksheet, 'assets/images/logo_large.png'
        )
        self.heading(
            workbook, worksheet, f'{org_name} Breakdown \n by [{question["input_type"]}] Question'
        )
        self.render_subheading(
            workbook, worksheet, f'[Question{question["sno"]}] {question["text"]}'
        )

        if question["input_type"] in ["checkbox", "radio", "dropdown"]:
            self.render_question_options(
                workbook, worksheet, question["obj"]
            )

        self.render_response_table(
            workbook, worksheet, all_orgs, question
        )
