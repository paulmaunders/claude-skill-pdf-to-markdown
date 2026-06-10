# Test Files

This directory contains test files for the PDF to Markdown skill.

## Test Documents

### sample-document.pdf (3 pages)
A comprehensive test document that includes:
- Multi-level headers (H1, H2)
- Paragraphs with line breaks (to test merging)
- Bold and italic formatting
- Unordered and ordered lists
- Simple tables
- Complex tables with multi-line cells (to test `<br>` tag cleanup)
- Multiple pages
- Code/monospace text

### large-document.pdf (35 pages)
A large test document for performance benchmarking that includes:
- 35 pages of varied content
- Multiple sections with headers and subheaders
- Tables with multi-line cells throughout
- Lists and formatted text
- Realistic document structure for testing performance

### scanned-document.pdf (1 page, image-only)
A "scanned" document with **no text layer** — the page is a raster image, so
standard extraction returns nothing and only OCR can recover the text. Used by
the OCR extraction tests (which skip automatically when Tesseract/OpenCV are
unavailable).

## Generating Test Documents

The test PDFs are generated programmatically using included scripts:

```bash
# Generate 2-page sample document
uv run --with reportlab -- python test-files/generate_sample_pdf.py

# Generate 35-page large document
uv run --with reportlab -- python test-files/generate_large_pdf.py

# Generate image-only scanned document (for OCR tests)
uv run --with pymupdf==1.27.2.3 -- python test-files/generate_scanned_pdf.py
```

This creates fresh PDFs with consistent, reproducible content.

## Testing Conversion

Test the conversion with:

```bash
# Convert to markdown
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py test-files/sample-document.pdf

# Output will be saved as test-files/sample-document.md
```

## Performance Benchmarking

Benchmark conversion performance:

```bash
uv run --with pymupdf4llm==0.3.4 -- python test-files/benchmark.py test-files/large-document.pdf
```

## What to Look For

After conversion, check that:
- Headers are properly formatted as markdown headers
- Table cells with `<br/>` tags are merged into single lines
- Paragraphs that span multiple lines are merged appropriately
- Lists are formatted correctly
- Bold and italic formatting is preserved
- Content from all pages is included
