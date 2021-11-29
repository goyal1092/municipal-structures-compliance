import random
from ..base import ReportingBase
from xlsxwriter.utility import xl_rowcol_to_cell

class ResultSummary(ReportingBase):

    def render_table_headings(
        self, workbook, worksheet, orgs, sections
    ):

        row = 3
        col = 2
        color = None
        for section in sections:
            new_color = random.choice(self.colors)
            while color == new_color:
                new_color = random.choice(self.colors)
            color = new_color
            merge_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'font_size': 18,
                'bg_color': color
            })
            from_cell = xl_rowcol_to_cell(row, col)
            to_cell = xl_rowcol_to_cell(row, col + len(section["questions"])-1)
            worksheet.set_column(f'{from_cell}:{to_cell}', 50)
            worksheet.set_row(row, 60)
            worksheet.merge_range(f'{from_cell}:{to_cell}', section["label"], merge_format)

            subcol = col

            cell_format_align = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'font_size': 14,
            })
            cell_format_align.set_bg_color('#C5C5C5')

            cell_format = workbook.add_format({
                'valign': 'vcenter',
                'border': 1,
                'font_size': 14,
                'bg_color': color
            })
            cell_format.set_text_wrap()


            for question in section["questions"]:
                worksheet.set_row(row+1, 40)
                worksheet.write(row+1, subcol, question["text"], cell_format)
                worksheet.write(row+2, subcol, question["label"], cell_format_align)
                subcol = subcol + 1

            col = col + len(section["questions"])


    def render_orgs(self, workbook, worksheet, orgs):
        heading_cell_format = workbook.add_format({
            'bold': True, 'font_size': 14,
            'font_name': self.font_name,
            'border': 1
        })
        heading_cell_format.set_text_wrap()
        heading_cell_format.set_align('center')
        heading_cell_format.set_align('vcenter')
        heading_cell_format.set_bg_color('#C5C5C5')

        row = 5
        col = 0
        worksheet.write(
            row,  col, 'Organisation Name',
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
            row = row + 1
            worksheet.set_row(row, 40)
            worksheet.write(
                row,  col,
                org.name, cell_format
            )

    def render_data(self, workbook, worksheet, sections, orgs):

        cell_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_size': 14,
        })

        row = 6
        questions = []
        for section in sections:
            questions = questions + section["questions"]

        for org in orgs:
            col = 2
            for question in questions:
                response = question["responses"].get(org.id , "-")
                if isinstance(response, list):
                    response = ",".join(response)
                worksheet.write(row, col, response, cell_format)
                col = col + 1
            row = row + 1


    def format(self, workbook, worksheet, org_name, orgs, sections):
        self.logo(
            workbook, worksheet, 'assets/images/logo_large.png'
        )
        self.heading(
            workbook, worksheet, f'{org_name}'
        )
        self.render_subheading(
            workbook, worksheet, 'Western Cape Form Result Summary'
        )

        self.render_table_headings(workbook, worksheet, orgs, sections)
        self.render_orgs(workbook, worksheet, orgs)
        self.render_data(workbook, worksheet, sections, orgs)
