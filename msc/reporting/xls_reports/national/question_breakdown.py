
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

    def render_response_table(self, workbook, worksheet, all_data, question):
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
        subcol = 0
        if question["input_type"] in ["radio", "dropdown", "checkbox"]:
            for idx, choice in enumerate(question["obj"].options.get("choices", [])):
                worksheet.set_column(subcol+1, subcol+1, 50)
                worksheet.write(
                    row,  subcol+1, f'Option{idx+1} [{choice}]',
                    heading_cell_format
                )

                subcol = subcol + 1
        elif question["input_type"] == "number":
            worksheet.set_column(subcol+1, subcol+1, 50)
            worksheet.write(
                row,  subcol+1, 'Number response (Total Sum)',
                heading_cell_format
            )
            subcol = subcol + 1
        worksheet.set_column(subcol+1, subcol+1, 50)
        worksheet.write(
            row,  subcol+1, 'Forms not Submitted (no. of orgs.)',
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

        row = row +1
        for data in all_data:
            questions = []
            for q in data["responses"]:
                questions = questions + q["questions"]

            worksheet.write(
                row,  col,
                data["label"], cell_format
            )
            subcol = 1
            question_obj = next(
                item for item in questions if item["id"] == question["id"]
            )
            if question["input_type"] in ["dropdown", "radio", "checkbox"]:
                for choice in question["obj"].options.get("choices", []):
                    worksheet.write(
                        row,  subcol,
                        f'{question_obj["grouped_value"].get(choice, 0)} ({choice})',
                        cell_format
                    )
                    subcol = subcol + 1
            elif question["input_type"] == "number":
                worksheet.write(
                    row,  subcol,
                    question_obj["grouped_value"],
                    cell_format
                )
                subcol = subcol + 1

            munis = data["muni_organisations"].count()
            submitted = data["submitted"].count()
            worksheet.write(
                row,  subcol,
                munis - submitted,
                cell_format
            )
            row = row + 1

    def format(self, workbook, worksheet, org_name, total_data, question):
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
            workbook, worksheet, total_data, question
        )
