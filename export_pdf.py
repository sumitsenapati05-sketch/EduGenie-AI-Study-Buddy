from fpdf import FPDF

def export_summary_to_pdf(summary_text, output_path="summary_output.pdf"):
    pdf = FPDF()
    pdf.add_page()
    # Add Unicode font (make sure the font file is in the folder or system)
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 10, summary_text)
    pdf.output(output_path)
    print(f"📄 PDF exported to: {output_path}")
