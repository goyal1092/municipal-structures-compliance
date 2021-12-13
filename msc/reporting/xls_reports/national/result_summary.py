import random
from ..base import ReportingBase
from xlsxwriter.utility import xl_rowcol_to_cell

class ResultSummary(ReportingBase):

    def render_questions(
        self, workbook, worksheet, sections
    ):
        row = 3
        col = 0
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
            merge_format.set_text_wrap()
            from_cell = xl_rowcol_to_cell(row, col)
            to_cell = xl_rowcol_to_cell(row + len(section["questions"])-1, col)
            worksheet.merge_range(
                f'{from_cell}:{to_cell}', section["label"], merge_format
            )

            subrow = row
            label_cell_format = workbook.add_format({
                'valign': 'vcenter',
                'border': 1,
                'font_size': 14,
                'align': 'center',
            })

            cell_format = workbook.add_format({
                'valign': 'vcenter',
                'border': 1,
                'font_size': 14
            })
            cell_format.set_text_wrap()
            label_cell_format.set_text_wrap()

            for question in section["questions"]:
                worksheet.set_column('B:B', 40)
                worksheet.set_column('C:C', 80)
                worksheet.set_row(subrow, 20)
                worksheet.write(subrow, col+1, str(question["sno"]), label_cell_format)
                worksheet.write(subrow, col+2, question["text"], cell_format)
                subrow = subrow + 1
            row = row + len(section["questions"]) + 1

    def render_orgs(self, workbook, worksheet, all_data):
        row = 1
        col = 3
        cell_format_align = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_size': 14,
        })

        cell_format = workbook.add_format({
            'valign': 'vcenter',
            'border': 1,
            'font_size': 14,
        })
        cell_format.set_bg_color('#C5C5C5')

        sub_cell_format = workbook.add_format({
            'valign': 'vcenter',
            'border': 1,
            'font_size': 14,
        })

        for data in all_data:
            munis = data["muni_organisations"].count()
            submitted = data["submitted"].count()
            worksheet.set_row(row, 60)
            worksheet.set_column(col, col, 70)
            worksheet.write(row, col, data["label"], cell_format_align)
            worksheet.write(
                row+1,
                col,
                f'Form Responses ({submitted}/{munis})',
                cell_format
            )
            subrow = 3
            for sec in data["responses"]:
                for q in sec["questions"]:
                    d = []
                    if q["input_type"] in ["dropdown", "radio", "checkbox"]:
                        for choice in q["obj"].options.get("choices", []):
                            d.append(f'{q["grouped_value"].get(choice, 0)} (choice)')

                    elif q["input_type"] == "number":
                        d.append(f'{q["grouped_value"]} (Total Sum)')
                    else:
                        d.append("View question summaries to view responses")
                    d.append(f' -  {munis}')
                    d.append(f'({munis-submitted} unsubmitted)')

                    worksheet.write(
                        subrow,
                        col,
                        str(" ".join(d)),
                        sub_cell_format
                    )
                    subrow = subrow + 1
            col = col + 1

    def format(self, workbook, worksheet, org_name, all_data, sections):
        self.logo(
            workbook, worksheet, 'assets/images/logo_large.png'
        )
        self.heading(
            workbook, worksheet, f'{org_name}'
        )
        self.render_subheading(
            workbook, worksheet, f'{org_name} Form Result Summary'
        )

        self.render_questions(workbook, worksheet, sections)
        self.render_orgs(workbook, worksheet, all_data)
