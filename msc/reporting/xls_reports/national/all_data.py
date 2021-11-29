
from ..base import ReportingBase
from xlsxwriter.utility import xl_rowcol_to_cell

class AllData(ReportingBase):

    headers = [
        "Province",
        "Organisation"
    ]

    def headings(self, workbook, worksheet, sections):
        row = 0
        col = 0
        heading_cell_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        headers = self.headers
        for heading in self.headers:
            worksheet.set_column(row, col, len(heading) + 10)
            worksheet.write(
                row, col,
                heading,
                heading_cell_format
            )
            col += 1

        merge_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
        })

        for section in sections:
            from_cell = xl_rowcol_to_cell(row, col)
            to_cell = xl_rowcol_to_cell(row, col + len(section["questions"])-1)
            worksheet.merge_range(f'{from_cell}:{to_cell}', section["label"], merge_format)

            subcol = col

            cell_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
            })

            for question in section["questions"]:
                worksheet.set_column(2, subcol, len(question["text"]) + 10)
                cell_format.set_text_wrap()
                worksheet.write(1, subcol, question["label"], cell_format)
                worksheet.write(2, subcol, question["text"], cell_format)
                subcol = subcol + 1

            col = col + len(section["questions"])

    def render_org_data(self, workbook, worksheet, all_data):
        row = 5
        cell_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
        })
        for data in all_data:
            for org in data["muni_organisations"]:
                worksheet.write(row, 0, data["label"], cell_format)
                worksheet.write(row, 1, org.name, cell_format)
                row = row + 1

    def render_data(self, workbook, worksheet, all_data, sections):

        cell_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
        })
        row = 5
        questions = []
        for section in sections:
            questions = questions + section["questions"]

        for data in all_data:
            responses = []
            for response in data["responses"]:
                responses = responses + response["questions"]

            for org in data["muni_organisations"]:
                col = 2
                for question in questions:
                    question_obj = next(
                        item for item in responses if item["id"] == question["id"]
                    )
                    response = question_obj["responses"].get(org.id , "-")
                    if isinstance(response, list):
                        response = ",".join(response)
                    worksheet.write(row, col, response, cell_format)
                    col = col + 1
                row = row + 1

    def format(self, workbook, worksheet, all_data, sections):
        self.headings(workbook, worksheet, sections)
        self.render_org_data(workbook, worksheet, all_data)
        self.render_data(workbook, worksheet, all_data, sections)
