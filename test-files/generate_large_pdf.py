#!/usr/bin/env python3
"""
Generate a large multi-page PDF for performance testing.

This creates a realistic 35-page document with:
- Multiple sections with headers
- Paragraphs with realistic content
- Tables on most pages
- Lists and formatting
- Mix of simple and complex content

Usage:
    uv run --with reportlab -- python test-files/generate_large_pdf.py
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


def create_large_pdf():
    """Generate a large 35-page PDF for performance testing."""

    output_path = Path(__file__).parent / "large-document.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    story = []
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

    # Title page
    story.append(Paragraph("Large Test Document", title_style))
    story.append(Paragraph("Performance Testing Reference", h2_style))
    story.append(Spacer(1, 0.5 * inch))

    intro = """
    This document is designed to test PDF to Markdown conversion performance on larger documents.
    It contains 35 pages of varied content including headers, paragraphs, tables, and lists.
    This simulates real-world documents such as technical reports, business documents, and
    comprehensive guides that need to be converted to markdown format for LLM processing.
    """
    story.append(Paragraph(intro, styles['Normal']))
    story.append(PageBreak())

    # Generate 34 more pages with varied content
    for section in range(1, 35):
        # Section header
        story.append(Paragraph(f"Section {section}: Content Analysis", h1_style))

        # Introduction paragraph
        section_intro = f"""
        This section explores various aspects of document processing and conversion methodologies.
        Section {section} focuses on demonstrating how the conversion handles mixed content types
        including structured data, narrative text, and formatted elements. The content has been
        designed to test edge cases and ensure robust handling of complex document structures.
        """
        story.append(Paragraph(section_intro, styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Subsection
        story.append(Paragraph(f"{section}.1 Technical Overview", h2_style))

        overview = """
        Modern document processing requires sophisticated algorithms to maintain fidelity when
        converting between formats. The extraction process must preserve semantic meaning while
        adapting to the constraints of the target format. This includes handling of whitespace,
        line breaks, table structures, and formatting elements that may not have direct equivalents
        in the destination format.
        """
        story.append(Paragraph(overview, styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Add a table every other section
        if section % 2 == 0:
            story.append(Paragraph(f"{section}.2 Data Summary", h2_style))

            table_data = [
                ['Metric', 'Value', 'Status', 'Notes'],
                [
                    'Processing Speed',
                    f'{section * 10} pages/sec',
                    'Optimal',
                    'Within expected range'
                ],
                [
                    'Accuracy Rate',
                    f'{95 + (section % 5)}%',
                    'Good',
                    'Meets quality standards'
                ],
                [
                    Paragraph('Memory Usage', styles['Normal']),
                    Paragraph(f'{section * 2}MB average<br/>peak usage tracked', styles['Normal']),
                    'Normal',
                    Paragraph('Efficient allocation<br/>and cleanup', styles['Normal'])
                ],
                [
                    'Error Rate',
                    f'{(section % 3) * 0.1}%',
                    'Excellent',
                    'Minimal issues detected'
                ],
            ]

            t = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.8*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.2 * inch))

        # Add lists periodically
        if section % 3 == 0:
            story.append(Paragraph(f"{section}.3 Key Considerations", h2_style))

            items = [
                ListItem(Paragraph("Maintain document structure and hierarchy during conversion", styles['Normal']), leftIndent=35),
                ListItem(Paragraph("Preserve formatting elements where possible in the target format", styles['Normal']), leftIndent=35),
                ListItem(Paragraph("Handle edge cases such as multi-line table cells and nested structures", styles['Normal']), leftIndent=35),
                ListItem(Paragraph("Optimize for both human readability and machine processing", styles['Normal']), leftIndent=35),
                ListItem(Paragraph("Ensure consistent output across different document types and sources", styles['Normal']), leftIndent=35),
            ]
            story.append(ListFlowable(items, bulletType='bullet'))
            story.append(Spacer(1, 0.2 * inch))

        # Additional content paragraph
        additional = f"""
        The conversion process for section {section} demonstrates the system's capability to handle
        varied content types. <b>Performance metrics</b> indicate that processing efficiency remains
        consistent even as document complexity increases. <i>Quality assurance</i> procedures verify
        that the output maintains fidelity to the source material while adapting appropriately to
        markdown format constraints.
        """
        story.append(Paragraph(additional, styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Summary paragraph before page break
        summary = """
        This section has covered the essential elements of document processing including structural
        analysis, data extraction, and format conversion. The methodologies presented here apply
        broadly across different document types and use cases, providing a foundation for robust
        document handling systems.
        """
        story.append(Paragraph(summary, styles['Normal']))

        # Page break (except for last page)
        if section < 34:
            story.append(PageBreak())

    # Build PDF
    doc.build(story)

    print(f"✓ Generated: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"  Pages: 35")
    print(f"\nTest with:")
    print(f"  uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py {output_path}")


if __name__ == "__main__":
    create_large_pdf()
