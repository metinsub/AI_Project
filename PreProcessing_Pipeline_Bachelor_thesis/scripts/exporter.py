from fpdf import FPDF
from scripts.logger.loggerSetup import setup_logger

logger = setup_logger(__name__)


def export_to_pdf(chunks, output_file):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Register Unicode Fonts (normal, bold, italic)
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)
    pdf.add_font("DejaVu", "I", "fonts/DejaVuSans-Oblique.ttf", uni=True)

    for chunk in chunks:
        header = chunk.get("header", "")
        rephrased_text = chunk.get("rephrased", "").replace("\t", "    ")

        # Header
        pdf.set_font("DejaVu", style="B", size=10)
        pdf.multi_cell(0, 10, f"Header: {header}")
        pdf.ln(2)

        # Rephrased Text
        if rephrased_text:
            pdf.set_font("DejaVu", style="I", size=7)
            pdf.multi_cell(0, 8, rephrased_text)
            pdf.ln(5)

    pdf.output(output_file)
    logger.info(f"PDF saved: {output_file}")
