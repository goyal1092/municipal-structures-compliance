

class ReportingBase:
    font_name = "Arial"
    excluded_question_types = ["longtext", "shorttext"]
    colors = [
        "#ffb3b3", "#ffc6b3", "#ffe699", "#d9ffb3", "#b3ffd9",
        "#b3ffff", "#b3ecff", "#c6b3ff", "#ecb3ff", "#ffb3d9",
        "#ffb3c6"
    ]

    color_code = {
        "All Data": "#ff4d4d",
        "Overview": "#ffa64d",
        "Complied - Yes": "#e6e600",
        "Complied - No": "#00cc00",
        "Result Summary": "#4d4dff",
        "Breakdown": "#d24dff",
    }

    def get_color_code(self, name):
        for key, val in self.color_code.items():
            if key in name:
                return val

    def create_sheet(self, workbook, name):
        worksheet = workbook.add_worksheet(name)
        color = self.get_color_code(name)
        if color:
            worksheet.set_tab_color(color)
        return worksheet

    def logo(self, workbook, worksheet, image):
        heading_cell_format = workbook.add_format()
        heading_cell_format.set_text_wrap()
        heading_cell_format.set_align('center')
        heading_cell_format.set_align('vcenter')
        worksheet.set_row(0, 140)
        worksheet.set_column('A:A', 70)
        worksheet.insert_image(0, 0, image, {'x_scale': 1, 'y_scale': 0.95})

    def heading(self, workbook, worksheet, heading):
        heading_cell_format = workbook.add_format({
            'bold': True,
            'font_name': self.font_name,
            'font_size': 14
        })
        heading_cell_format.set_text_wrap()
        heading_cell_format.set_align('center')
        heading_cell_format.set_align('vcenter')
        worksheet.set_column('B:B', 30)
        worksheet.write(
            0, 1, heading, heading_cell_format
        )

    def render_subheading(self, workbook, worksheet, heading):
        heading_cell_format = workbook.add_format({
            'bold': True,
            'font_name': self.font_name,
            'font_size': 14,
            'font_color': '#ff9900'
        })
        heading_cell_format.set_text_wrap()
        heading_cell_format.set_align('center')
        heading_cell_format.set_align('vcenter')
        worksheet.write(
            1, 0, heading, heading_cell_format
        )
