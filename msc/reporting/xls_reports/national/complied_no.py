
from ..base import ReportingBase

class CompliedNo(ReportingBase):

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

        cell_format = workbook.add_format({
            'bold': True, 'font_size': 14,
            'font_name': self.font_name,
            'border': 1
        })
        cell_format.set_text_wrap()
        cell_format.set_align('center')
        cell_format.set_align('vcenter')

        for d in data:
            if not d["complied"]:
                row = row + 1
                worksheet.write(
                    row,  col,
                    d["label"], cell_format
                )

    def format(self, workbook, worksheet, org_name, data):
        self.logo(
            workbook, worksheet, 'assets/images/logo_large.png'
        )
        self.heading(
            workbook, worksheet, f'{org_name}'
        )
        self.render_table(
            workbook, worksheet, data
        )
