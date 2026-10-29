import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from app.core.config import settings

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (on pages after the first)
        if self._pageNumber > 1:
            self.drawString(54, 750, "EduAI Learning Platform — Smart Study Notes")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 612 - 54, 742)
            
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, footer_text)
        self.drawString(54, 36, "Confidential & Proprietary — For Academic Use Only")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 612 - 54, 48)
        self.restoreState()


def clean_markdown_for_pdf(text: str) -> str:
    """Removes or converts markdown tags to ReportLab paragraph compatible markup."""
    # Convert bold **text** to <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Convert italic *text* to <i>text</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Convert inline code `text` to <b><font color="#4F46E5">text</font></b>
    text = re.sub(r'`(.*?)`', r'<b><font color="#4F46E5">\1</font></b>', text)
    # Strip LaTeX $ wrappers for clean printing
    text = text.replace('$$', '').replace('$', '')
    # Escape ampersands if not already XML entity
    text = text.replace('&', '&amp;') if '&amp;' not in text else text
    return text


def generate_smart_notes_pdf(
    course_title: str,
    section_title: str,
    objectives: list,
    content: str,
    summary: str = "",
    output_filename: str = ""
) -> str:
    """
    Generates a publication-grade Smart Notes PDF for a course section.
    Returns the absolute path to the generated PDF.
    """
    if not output_filename:
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', f"{course_title}_{section_title}")[:40]
        output_filename = f"notes_{safe_name}.pdf"
    
    output_path = os.path.join(settings.NOTES_DIR, output_filename)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#4F46E5")     # Indigo
    c_dark = colors.HexColor("#172033")        # Slate 900
    c_muted = colors.HexColor("#64748B")       # Slate 500
    c_border = colors.HexColor("#E2E8F0")      # Slate 200
    c_card_bg = colors.HexColor("#F8FAFC")     # Slate 50
    c_tip_bg = colors.HexColor("#EEF2FF")      # Indigo 50
    c_tip_border = colors.HexColor("#818CF8")  # Indigo 400
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_dark
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=c_primary
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=c_muted
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_dark,
        spaceBefore=14,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155")
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=15
    )
    
    tip_style = ParagraphStyle(
        'TipText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#312E81")
    )

    story = []
    
    # 1. Header Box
    header_content = [
        [
            Paragraph("<b>EDUAI ACADEMIC SMART NOTES</b>", subtitle_style),
            Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", meta_style)
        ],
        [
            Paragraph(course_title, title_style),
            Paragraph("University Curriculum Series", meta_style)
        ],
        [
            Paragraph(f"Section Topic: <b>{section_title}</b>", subtitle_style),
            ""
        ]
    ]
    header_table = Table(header_content, colWidths=[380, 124])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=8, spaceAfter=14))
    
    # 2. Executive Summary Box
    if summary:
        summary_p = Paragraph(f"<b>Executive Summary:</b> {clean_markdown_for_pdf(summary)}", body_style)
        summary_table = Table([[summary_p]], colWidths=[504])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
            ('BOX', (0,0), (-1,-1), 1, c_border),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 12))
    
    # 3. Learning Objectives Section
    if objectives:
        story.append(Paragraph("1. Core Learning Objectives", h1_style))
        obj_items = []
        for obj in objectives:
            p = Paragraph(f"• {clean_markdown_for_pdf(obj)}", bullet_style)
            obj_items.append([p])
        obj_table = Table(obj_items, colWidths=[504])
        obj_table.setStyle(TableStyle([
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(obj_table)
        story.append(Spacer(1, 10))

    # 4. Detailed Section Breakdown from Content
    story.append(Paragraph("2. Conceptual Breakdown & Technical Formulations", h1_style))
    
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('### '):
            story.append(Spacer(1, 6))
            story.append(Paragraph(clean_markdown_for_pdf(stripped[4:]), ParagraphStyle('H3', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=c_primary)))
            story.append(Spacer(1, 3))
        elif stripped.startswith('## '):
            story.append(Spacer(1, 8))
            story.append(Paragraph(clean_markdown_for_pdf(stripped[3:]), ParagraphStyle('H2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=c_dark)))
            story.append(Spacer(1, 4))
        elif stripped.startswith('# '):
            pass # skip top h1
        elif stripped.startswith('- ') or stripped.startswith('* '):
            story.append(Paragraph(f"• {clean_markdown_for_pdf(stripped[2:])}", bullet_style))
            story.append(Spacer(1, 2))
        elif 'tip' in stripped.lower() or 'exam' in stripped.lower() or 'note:' in stripped.lower():
            tip_p = Paragraph(f"<b>Exam Note:</b> {clean_markdown_for_pdf(stripped)}", tip_style)
            tip_t = Table([[tip_p]], colWidths=[504])
            tip_t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), c_tip_bg),
                ('BOX', (0,0), (-1,-1), 1, c_tip_border),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(Spacer(1, 4))
            story.append(tip_t)
            story.append(Spacer(1, 4))
        elif stripped.startswith('```'):
            continue
        else:
            story.append(Paragraph(clean_markdown_for_pdf(stripped), body_style))
            story.append(Spacer(1, 4))

    # 5. Study Guide & Practice Questions
    story.append(Spacer(1, 10))
    story.append(Paragraph("3. Self-Assessment & Exam Checklist", h1_style))
    checklist_data = [
        [Paragraph("<b>Topic Milestone</b>", body_style), Paragraph("<b>Mastery Check</b>", body_style)],
        [Paragraph("Can you formulate the primary mathematical loss / model objective?", bullet_style), Paragraph("[  ] Confirmed", bullet_style)],
        [Paragraph("Can you distinguish parametric vs non-parametric assumptions?", bullet_style), Paragraph("[  ] Confirmed", bullet_style)],
        [Paragraph("Are you prepared to calculate precision, recall, and F1 metrics?", bullet_style), Paragraph("[  ] Confirmed", bullet_style)],
        [Paragraph("Do you understand the difference between L1 sparsity and L2 shrinkage?", bullet_style), Paragraph("[  ] Confirmed", bullet_style)]
    ]
    check_table = Table(checklist_data, colWidths=[380, 124])
    check_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(check_table)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_path


def generate_course_certificate_pdf(
    student_name: str,
    course_title: str,
    certificate_uid: str,
    completion_date: str = "",
    output_filename: str = ""
) -> str:
    """
    Generates an official landscape PDF Certificate of Completion.
    """
    if not output_filename:
        output_filename = f"certificate_{certificate_uid}.pdf"
    output_path = os.path.join(settings.CERTIFICATES_DIR, output_filename)
    
    if not completion_date:
        completion_date = datetime.now().strftime("%B %d, %Y")
    
    # 11 x 8.5 landscape
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    c_gold = colors.HexColor("#D97706")
    c_indigo = colors.HexColor("#312E81")
    c_dark = colors.HexColor("#0F172A")
    c_slate = colors.HexColor("#475569")
    
    cert_title = ParagraphStyle(
        'CertTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=c_indigo,
        alignment=1 # Center
    )
    
    cert_subtitle = ParagraphStyle(
        'CertSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_gold,
        alignment=1
    )
    
    cert_recipient = ParagraphStyle(
        'CertRecipient',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=c_dark,
        alignment=1
    )
    
    cert_body = ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=18,
        textColor=c_slate,
        alignment=1
    )
    
    cert_course = ParagraphStyle(
        'CertCourse',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=24,
        textColor=colors.HexColor("#4F46E5"),
        alignment=1
    )
    
    story = [
        Spacer(1, 15),
        Paragraph("EDUAI UNIVERSITY LEARNING PLATFORM", cert_subtitle),
        Spacer(1, 10),
        Paragraph("CERTIFICATE OF ACADEMIC ACHIEVEMENT", cert_title),
        Spacer(1, 6),
        HRFlowable(width="60%", thickness=2, color=c_gold, spaceBefore=4, spaceAfter=18),
        Paragraph("THIS IS PROUDLY CONFERRED UPON", cert_body),
        Spacer(1, 10),
        Paragraph(student_name, cert_recipient),
        Spacer(1, 10),
        Paragraph(
            "for successfully completing all curriculum requirements, continuous interactive assessments, "
            "and mastery benchmarks in the advanced university course:",
            cert_body
        ),
        Spacer(1, 12),
        Paragraph(course_title, cert_course),
        Spacer(1, 24)
    ]
    
    # Signature & Verification block
    sig_data = [
        [
            Paragraph("<b>Dr. Marcus Vance, Ph.D.</b><br/><font color='#64748B'>Academic Director &amp; Dean of AI</font>", ParagraphStyle('Sig1', parent=styles['Normal'], alignment=1, fontSize=10, leading=14)),
            Paragraph(f"<b>EduAI Gold Seal of Verification</b><br/><font color='#D97706'>[ Verified Academic Record ]</font>", ParagraphStyle('Seal', parent=styles['Normal'], alignment=1, fontSize=10, leading=14)),
            Paragraph(f"<b>Issue Date: {completion_date}</b><br/><font color='#64748B'>Certificate UID: {certificate_uid}</font>", ParagraphStyle('Sig2', parent=styles['Normal'], alignment=1, fontSize=10, leading=14))
        ]
    ]
    sig_table = Table(sig_data, colWidths=[240, 240, 240])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEABOVE', (0,0), (0,0), 1, colors.HexColor("#94A3B8")),
        ('LINEABOVE', (2,0), (2,0), 1, colors.HexColor("#94A3B8")),
    ]))
    story.append(sig_table)
    
    doc.build(story)
    return output_path
