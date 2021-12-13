
from ..base import ReportingBase

class Cover(ReportingBase):

    def heading(self, workbook, worksheet, org_name):
        heading_cell_format = workbook.add_format({
            'bold': True, 'font_color': '#ff9900', 'font_size': 46,
            'font_name': self.font_name
        })
        heading_cell_format.set_text_wrap()
        heading_cell_format.set_align('center')
        heading_cell_format.set_align('vcenter')
        worksheet.set_row(0, 200)
        worksheet.set_column('A:A', 130)
        worksheet.set_column('B:B', 30)
        worksheet.write(
            0, 0,
            f'{org_name} Compliance Monitoring Workbook',
            heading_cell_format
        )

    def logo(self, workbook, worksheet, image):
        worksheet.set_row(2, 180)
        worksheet.set_column('A:A', 120)
        worksheet.insert_image(2, 0, image, {'x_scale': 1.7, 'y_scale': 1.2})

    def content_table(self, workbook, worksheet):
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 16,
        })
        worksheet.merge_range('A6:B6', 'Cover Page', merge_format)

    def add_link(self, workbook, worksheet, row, col, sheet_name):
        color = self.get_color_code(sheet_name)
        cell_format = workbook.add_format({
            'bold': True, 'font_size': 18,
            'font_name': self.font_name,
            'border': 1, 'bg_color': color,
        })
        cell_format.set_align('center')
        cell_format.set_align('vcenter')

        url_format = workbook.add_format({
            'font_name': self.font_name,
            'border': 1, 'bg_color': '#C5C5C5',
            'font_size': 16,
        })
        url_format.set_align('center')
        url_format.set_align('vcenter')

        display_name = sheet_name
        if "Breakdown" in sheet_name:
            display_name = "Breakdown of Questions"
        worksheet.write(row, col, display_name, cell_format)
        worksheet.set_row(row, 30)
        worksheet.write_url(row, col+1, f"internal:'{sheet_name}'!A1", url_format, string="Link to Tab")

    def format(self, workbook, worksheet, org_name):
        self.heading(workbook, worksheet, org_name)
        self.logo(
            workbook, worksheet, 'assets/images/logo_large.png'
        )
        self.content_table(workbook, worksheet)
