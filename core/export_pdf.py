from fpdf import FPDF

def export_summary_to_pdf(summary, filename="summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font("DejaVu", size=12)
    for line in summary.split("\n"):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
