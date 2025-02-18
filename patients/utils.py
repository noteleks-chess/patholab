from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_report_pdf(report, response):
    """Generates a PDF report for the given report object."""

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Add report content (example)
    story.append(Paragraph(f"Report for Test Order: {report.test_order}", styles['h1']))
    story.append(Spacer(1, 12))  # Add some space

    # Add other report details (e.g., patient info, test results, comments)
    story.append(Paragraph(f"Patient: {report.test_order.specimen.patient}", styles['Normal']))
    story.append(Paragraph(f"Comments: {report.comments_conclusion}", styles['Normal']))
    # ... add other details

    doc.build(story)
