#!/usr/bin/env python3
"""
Generate a sample PDF for testing the PDF to Markdown conversion.

This creates a comprehensive test document with:
- Multi-level headers
- Paragraphs with line breaks (to test merging)
- Tables with multi-line cells (to test <br> tag cleanup)
- Lists (ordered and unordered)
- Bold and italic text
- Multiple pages

Usage:
    uv run --with reportlab -- python test-files/generate_sample_pdf.py
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from pathlib import Path


def create_sample_pdf():
    """Generate a comprehensive sample PDF for testing."""

    output_path = Path(__file__).parent / "sample-document.pdf"

    # Create the PDF document
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Container for the 'Flowable' objects
    story = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=12,
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=10,
    )

    # Title
    story.append(Paragraph("Sample Test Document", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Introduction paragraph
    intro_text = """
    This is a comprehensive test document designed to verify PDF to Markdown conversion capabilities.
    It includes various formatting elements such as headers, paragraphs, tables, and lists.
    This paragraph intentionally spans multiple lines to test how the conversion handles text that
    continues across line breaks within the PDF structure.
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 1: Headers and Paragraphs
    story.append(Paragraph("1. Document Structure", h1_style))

    story.append(Paragraph("1.1 Multi-level Headers", h2_style))

    para1 = """
    This section demonstrates how different heading levels are preserved during conversion.
    The extraction process should maintain the hierarchical structure of the document,
    converting PDF text styling into appropriate markdown header levels.
    """
    story.append(Paragraph(para1, styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # Section 2: Formatting
    story.append(Paragraph("2. Text Formatting", h1_style))

    formatted_text = """
    This paragraph contains <b>bold text</b>, <i>italic text</i>, and <b><i>bold italic text</i></b>.
    The conversion process should preserve these formatting elements in the markdown output,
    using appropriate markdown syntax for emphasis and strong emphasis.
    """
    story.append(Paragraph(formatted_text, styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 3: Lists
    story.append(Paragraph("3. Lists and Enumeration", h1_style))

    story.append(Paragraph("3.1 Unordered List", h2_style))

    unordered_items = [
        ListItem(Paragraph("First item in the unordered list", styles['Normal']), leftIndent=35),
        ListItem(Paragraph("Second item with more details about the content", styles['Normal']), leftIndent=35),
        ListItem(Paragraph("Third item demonstrating list formatting", styles['Normal']), leftIndent=35),
    ]
    story.append(ListFlowable(unordered_items, bulletType='bullet'))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("3.2 Ordered List", h2_style))

    ordered_items = [
        ListItem(Paragraph("First numbered item", styles['Normal']), leftIndent=35),
        ListItem(Paragraph("Second numbered item", styles['Normal']), leftIndent=35),
        ListItem(Paragraph("Third numbered item", styles['Normal']), leftIndent=35),
    ]
    story.append(ListFlowable(ordered_items, bulletType='1'))
    story.append(Spacer(1, 0.3 * inch))

    # Section 4: Tables
    story.append(Paragraph("4. Tables and Data", h1_style))

    story.append(Paragraph("4.1 Simple Table", h2_style))

    # Simple table
    simple_data = [
        ['Feature', 'Status', 'Priority'],
        ['Header Extraction', 'Implemented', 'High'],
        ['Table Processing', 'Implemented', 'High'],
        ['List Formatting', 'Implemented', 'Medium'],
    ]

    simple_table = Table(simple_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
    simple_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    story.append(simple_table)
    story.append(Spacer(1, 0.3 * inch))

    # Complex table with multi-line cells
    story.append(Paragraph("4.2 Complex Table with Multi-line Cells", h2_style))

    para_text = """
    The table below contains cells with multiple lines of text. This tests the conversion's ability
    to handle complex table structures and merge multi-line content appropriately.
    """
    story.append(Paragraph(para_text, styles['Normal']))
    story.append(Spacer(1, 0.1 * inch))

    complex_data = [
        ['Component', 'Description', 'Notes'],
        [
            'PDF Parser',
            Paragraph('Extracts text and<br/>structure from PDF<br/>documents', styles['Normal']),
            Paragraph('Uses PyMuPDF4LLM<br/>for fast extraction', styles['Normal'])
        ],
        [
            'Table Processor',
            Paragraph('Cleans and formats<br/>table cell content<br/>removing HTML tags', styles['Normal']),
            Paragraph('Merges multi-line<br/>cells automatically', styles['Normal'])
        ],
        [
            'Markdown Generator',
            Paragraph('Converts extracted<br/>content to clean<br/>markdown format', styles['Normal']),
            Paragraph('Optimized for<br/>LLM consumption', styles['Normal'])
        ],
    ]

    complex_table = Table(complex_data, colWidths=[1.8*inch, 2.2*inch, 2*inch])
    complex_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))

    story.append(complex_table)

    # Page break
    story.append(PageBreak())

    # Page 2
    story.append(Paragraph("5. Continuous Content", h1_style))

    page2_text = """
    This is the second page of the test document. It demonstrates how the PDF to Markdown conversion
    handles content that spans multiple pages. The conversion should maintain document flow and
    properly handle page boundaries without losing content or introducing artifacts.
    """
    story.append(Paragraph(page2_text, styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("5.1 Code and Technical Content", h2_style))

    code_example = """
    Technical documentation often includes code examples or monospace text.
    For example: <font name="Courier">import pymupdf4llm</font> or command-line
    instructions like <font name="Courier">python script.py --option value</font>.
    """
    story.append(Paragraph(code_example, styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("5.2 Summary Table", h2_style))

    summary_data = [
        ['Test Category', 'Elements Tested', 'Expected Outcome'],
        ['Structure', 'Headers (H1, H2)', 'Markdown headers (#, ##)'],
        ['Formatting', 'Bold, Italic', 'Markdown emphasis (**, *)'],
        ['Lists', 'Ordered, Unordered', 'Markdown lists (-, 1.)'],
        ['Tables', 'Simple, Complex', 'Markdown tables with clean cells'],
        ['Pages', 'Multi-page', 'Continuous content flow'],
    ]

    summary_table = Table(summary_data, colWidths=[1.8*inch, 2.2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FCE4EC')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 0.5 * inch))

    # Conclusion
    story.append(Paragraph("6. Conclusion", h1_style))

    conclusion = """
    This sample document provides a comprehensive test case for PDF to Markdown conversion.
    It exercises all major features including text extraction, formatting preservation,
    table processing with multi-line cell cleanup, list handling, and multi-page document processing.
    The resulting markdown should be clean, well-structured, and optimized for consumption by
    large language models.
    """
    story.append(Paragraph(conclusion, styles['Normal']))

    # Build PDF
    doc.build(story)

    print(f"✓ Generated: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"\nTest with:")
    print(f"  uv run --with pymupdf4llm -- python scripts/pdf_to_markdown_pymupdf.py {output_path}")


if __name__ == "__main__":
    create_sample_pdf()
