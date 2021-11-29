
from ..base import ReportingBase

class ComplianceOverview(ReportingBase):

    def render_table(self, workbook, worksheet, data):
        heading_cell_format = workbook.add_format({
            'bold': True, 'font_size': 14,
            'font_name': self.font_name,
            'border': 1
        })
        heading_cell_format.set_text_wrap()
        heading_cell_format.set_align('center')
        heading_cell_format.set_align('vcenter')
        heading_cell_format.set_bg_color('#C5C5C5')

        row = 4
        col = 0
        worksheet.write(
            row,  col, 'Name of organisation',
            heading_cell_format
        )

        worksheet.write(
            row,  col+1, 'National Breakdown',
            heading_cell_format
        )

        cell_format = workbook.add_format({
            'bold': True, 'font_size': 14,
            'font_name': self.font_name,
            'border': 1, 'align': 'center',
            'valign': 'center'
        })

        cell_format_red = workbook.add_format({
            'bold': True, 'font_size': 14,
            'font_name': self.font_name,
            'border': 1, 'bg_color': '#ffb3b3',
            'align': 'center', 'valign': 'center'
        })

        cell_format_green = workbook.add_format({
            'bold': True, 'font_size': 14,
            'font_name': self.font_name,
            'border': 1, 'bg_color': '#b3ffc6',
            'align': 'center', 'valign': 'center'
        })
        cell_format.set_text_wrap()

        for d in data:
            row = row + 1
            worksheet.write(
                row,  col,
                d["label"], cell_format
            )

            submitted = d["submitted"].count()
            total = d["muni_organisations"].count()

            if d["complied"]:
                worksheet.write(
                    row,  col+1,
                    f'{submitted}/{total}', cell_format_green
                )
            else:
                worksheet.write(
                    row,  col+1,
                    f'{submitted}/{total}', cell_format_red
                )

    def format(self, workbook, worksheet, org_name, data):
        self.logo(
            workbook, worksheet, 'assets/images/logo_large.png'
        )
        self.heading(
            workbook, worksheet, f'{org_name}\n Compliance Overview'
        )
        self.render_table(
            workbook, worksheet, data
        )
