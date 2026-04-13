import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_review_report(data: dict, output_path: str) -> str:
    """Creates a professional DOCX review report."""
    doc = Document()
    
    # Title
    title = doc.add_heading('Research Paper Review Report', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Summary Section
    doc.add_heading('1. Overall Summary', level=1)
    doc.add_paragraph(data.get('final_verdict', 'Analysis complete.'))

    # Section Scores
    doc.add_heading('2. Section Scores', level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Section Name'
    hdr_cells[1].text = 'Score (0-10)'
    
    for section in data.get('section_analysis', []):
        row_cells = table.add_row().cells
        row_cells[0].text = section['title']
        row_cells[1].text = str(section['score'])

    # Strengths
    doc.add_heading('3. Key Strengths', level=1)
    for s in data.get('strengths', []):
        doc.add_paragraph(s, style='List Bullet')

    # Weaknesses
    doc.add_heading('4. Areas for Improvement', level=1)
    for w in data.get('weaknesses', []):
        doc.add_paragraph(w, style='List Bullet')

    # Suggestions
    doc.add_heading('5. Actionable Suggestions', level=1)
    for sug in data.get('suggestions', []):
        doc.add_paragraph(sug, style='List Bullet')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path
