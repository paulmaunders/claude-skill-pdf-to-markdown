---
name: pdf-to-markdown
description: Convert PDF documents to markdown format optimised for LLM consumption. Use when extracting text from PDFs, analyzing PDF content, or preparing PDFs for processing. Automatically cleans table cells and merges paragraph lines.
---

# PDF to Markdown Conversion

## Quick Start

For most PDFs, use PyMuPDF4LLM (instant extraction):

```bash
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py input.pdf
```

Output will be saved as `input.md` in the same directory.

**Note**: Scripts use relative paths from the skill directory. When running commands, ensure you're in the skill directory or adjust paths accordingly.

## Requirements

This skill uses `uv` to manage dependencies automatically.

**Dependencies** (installed on-demand via `uv run --with`):
- `pymupdf4llm==0.3.4` - Fast PDF extraction (required)
- `pymupdf-layout==1.27.2.3` - OCR-capable layout engine, used only with `--ocr` (required for the documented commands)
- `opencv-python` - Required for OCR support (optional)

No pre-installation needed - `uv run --with` installs packages temporarily when scripts execute.

**Note**: Versions are pinned so output stays reproducible. The script uses two extraction engines: the legacy engine (default) preserves multi-level header hierarchy (`#`/`##`/`###`); the ML layout engine (used only with `--ocr`) can read scanned pages but flattens all headers to `##`. Newer pymupdf4llm releases (1.27.x+) force the layout engine unconditionally, which is why `pymupdf4llm` is pinned to 0.3.4.

## Features

- **Clean table cells**: Removes `<br>` tags and merges multi-line content
- **Merged paragraphs**: Combines lines that end mid-sentence for continuous text
- **Structure preservation**: Keeps headers, lists, tables, code blocks intact
- **Batch processing**: Process entire directories of PDFs
- **OCR support**: Extract text from scanned/image-based PDFs via Tesseract
- **LLM-optimised**: Output designed for easy LLM consumption

## Usage Examples

### Single file
```bash
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py document.pdf
```

### Single file with custom output
```bash
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py input.pdf -o output.md
```

### Batch process directory
```bash
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py pdfs/ -o markdown/
```

### Keep original line breaks (disable merging)
```bash
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py input.pdf --no-merge
```

### Page chunks (separate markdown per page)
```bash
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py input.pdf --page-chunks
```

## OCR Support (Scanned PDFs)

For scanned documents or image-heavy PDFs where standard text extraction fails, enable OCR:

### Basic OCR
```bash
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 --with opencv-python -- python scripts/pdf_to_markdown_pymupdf.py scanned.pdf --ocr
```

### With Language Support
```bash
# German documents
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 --with opencv-python -- python scripts/pdf_to_markdown_pymupdf.py document.pdf --ocr --ocr-language deu

# Multi-language (English + German)
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 --with opencv-python -- python scripts/pdf_to_markdown_pymupdf.py document.pdf --ocr --ocr-language eng+deu
```

### OCR Options
- `--ocr` - Enable OCR for scanned/image-based pages
- `--ocr-language` - Tesseract language code (default: `eng`)
- `--ocr-dpi` - OCR resolution in DPI (default: 400, higher = more accurate but slower)

### System Requirements

OCR requires Tesseract to be installed:
- **macOS**: `brew install tesseract`
- **Ubuntu/Debian**: `sudo apt install tesseract-ocr`
- **Windows**: Download from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)

For additional languages, install language packs:
- **macOS**: `brew install tesseract-lang`
- **Ubuntu**: `sudo apt install tesseract-ocr-deu` (for German, etc.)

### How OCR Works

When `--ocr` is enabled, pymupdf-layout automatically:
1. Analyzes each page to determine if OCR is needed
2. Applies OCR only to pages with little/no extractable text
3. Text-based pages are processed normally (faster)

This means you can safely use `--ocr` on mixed documents - it won't slow down pages that don't need it.

**Caveat**: the OCR layout engine flattens all headers to `##` (it detects *that* a line is a heading, not its level). Multi-level header hierarchy is only preserved in the default (non-OCR) mode, so use `--ocr` only when a document actually needs it.

## How It Works

### PyMuPDF4LLM Processing
1. Extracts PDF content using PyMuPDF4LLM library
2. Cleans table cells by replacing `<br>` tags with spaces
3. Merges paragraph lines that end mid-sentence
4. Preserves special formatting (headers, lists, tables, code blocks)
5. Outputs GitHub-compatible markdown

### What Gets Preserved
- Headers (lines starting with `#`)
- Lists (ordered and unordered)
- Tables (with cleaned cell content)
- Code blocks
- Blockquotes
- Bold and italic formatting

### What Gets Merged
- Paragraph lines that end mid-sentence
- Table cell content with `<br>` tags
- Multi-line text blocks

## Common Patterns

When a user mentions PDFs or needs to extract text from documents, use this skill automatically:

```bash
# User: "Extract text from this PDF document"
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py document.pdf

# User: "Convert all PDFs in this folder to markdown"
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py pdfs/ -o markdown/

# User: "I need to analyze this PDF document"
# First convert to markdown, then analyze
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py document.pdf

# User: "This PDF looks like a scan, the text extraction isn't working well"
# Use OCR for scanned documents
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 --with opencv-python -- python scripts/pdf_to_markdown_pymupdf.py scanned.pdf --ocr

# Test with the included sample:
uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py test-files/sample-document.pdf
```

## Tips

- If standard extraction produces garbled or minimal output, try `--ocr` for scanned PDFs
- For multi-page tables, content may span across page breaks (this is normal)
- Table cell truncation at page boundaries reflects the PDF structure
- The `--no-merge` flag preserves original line breaks if needed
