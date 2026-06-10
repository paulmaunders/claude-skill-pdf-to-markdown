# PDF to Markdown - Claude Code Skill

A Claude Code Skill for converting PDF documents to clean, LLM-optimised markdown format.

## Features

- **Fast extraction**: Instant conversion using PyMuPDF4LLM
- **Clean table cells**: Automatically removes `<br>` tags and merges multi-line content
- **Merged paragraphs**: Combines lines that end mid-sentence for continuous text
- **Structure preservation**: Keeps headers, lists, tables, and code blocks intact
- **OCR support**: Extract text from scanned/image-based PDFs via Tesseract
- **Batch processing**: Convert entire directories of PDFs
- **LLM-optimised**: Output designed for easy consumption by language models

## Installation

### 1. Clone this repository

```bash
cd ~/Projects
git clone https://github.com/paulmaunders/claude-skill-pdf-to-markdown.git
```

### 2. Create symlink to Claude Code skills directory

```bash
ln -s ~/Projects/claude-skill-pdf-to-markdown ~/.claude/skills/pdf-to-markdown
```

### 3. Verify installation

The skill will be automatically available in Claude Code. You can verify by checking:

```bash
ls -la ~/.claude/skills/pdf-to-markdown
```

## Usage

Once installed, Claude Code will automatically use this skill when you mention PDFs or document extraction.

### Manual Usage

#### Convert single PDF
```bash
uv run --with pymupdf4llm==1.27.2.3 --with pymupdf-layout==1.27.2.3 -- python ~/.claude/skills/pdf-to-markdown/scripts/pdf_to_markdown_pymupdf.py document.pdf
```

#### Batch process directory
```bash
uv run --with pymupdf4llm==1.27.2.3 --with pymupdf-layout==1.27.2.3 -- python ~/.claude/skills/pdf-to-markdown/scripts/pdf_to_markdown_pymupdf.py pdfs/ -o markdown/
```

#### Options
- `-o, --output`: Output file or directory
- `--page-chunks`: Generate separate markdown file per page
- `--no-merge`: Don't merge paragraph lines (keep original line breaks)
- `--ocr`: Enable OCR for scanned/image-based pages (requires Tesseract)
- `--ocr-language`: Tesseract language code (default: eng)
- `--ocr-dpi`: OCR resolution in DPI (default: 400)

#### OCR for Scanned PDFs

```bash
# Requires Tesseract: brew install tesseract (macOS)
uv run --with pymupdf4llm==1.27.2.3 --with pymupdf-layout==1.27.2.3 --with opencv-python -- python ~/.claude/skills/pdf-to-markdown/scripts/pdf_to_markdown_pymupdf.py scanned.pdf --ocr
```

## How It Works

1. **Metadata loaded at startup** (minimal token cost)
   - Claude knows the skill exists and when to use it

2. **Instructions loaded when triggered**
   - SKILL.md loads into context when you mention PDFs

3. **Scripts executed as needed**
   - Python scripts run via bash without loading code into context
   - Only script output consumes tokens

## What Gets Processed

### Preserved
- Headers (lines starting with `#`)
- Lists (ordered and unordered)
- Tables (with cleaned cell content)
- Code blocks
- Blockquotes
- Bold and italic formatting

### Merged
- Paragraph lines that end mid-sentence
- Table cell content with `<br>` tags
- Multi-line text blocks

## Tool

### PyMuPDF4LLM
- **Speed**: Instant (~0 seconds per page)
- **Quality**: Excellent for most documents
- **OCR**: Built-in support for scanned documents via Tesseract
- **Use for**: Insurance docs, contracts, reports, forms, scanned documents

## Example Output

Using the included test document (`test-files/sample-document.pdf`):

**Before** (from PyMuPDF4LLM raw output):
```markdown
|Component|Description|Notes|
|---|---|---|
|PDF Parser|Extracts text and<br/>structure from PDF<br/>documents|Uses PyMuPDF4LLM<br/>for fast extraction|
```

**After** (with our cleanup):
```markdown
|Component|Description|Notes|
|---|---|---|
|PDF Parser|Extracts text and structure from PDF documents|Uses PyMuPDF4LLM for fast extraction|
```

## Project Structure

```
claude-skill-pdf-to-markdown/
├── SKILL.md                           # Main skill file (Claude reads this)
├── README.md                          # This file
├── LICENSE                            # AGPL-3.0 license
├── scripts/
│   └── pdf_to_markdown_pymupdf.py    # PDF extraction with OCR support
├── tests/
│   └── test_conversion.py             # Integration tests
└── test-files/
    └── sample-document.pdf            # Test document
```

## Development

### Running Tests

Run the integration test suite with:

```bash
uv run --with pymupdf4llm==1.27.2.3 --with pymupdf-layout==1.27.2.3 --with pytest -- pytest tests/ -v
```

### Testing Changes Manually

After modifying scripts, test with:

```bash
uv run --with pymupdf4llm==1.27.2.3 --with pymupdf-layout==1.27.2.3 -- python scripts/pdf_to_markdown_pymupdf.py test.pdf
```

### Contributing

1. Make changes in this directory
2. Test thoroughly with various PDF types
3. Update documentation as needed
4. Commit and push changes

The symlink ensures changes are immediately available in Claude Code.

## Requirements

- Python 3.8+
- uv (for dependency management)
- Libraries installed on-demand via `uv run --with` (pinned for reproducible output):
  - pymupdf4llm==1.27.2.3
  - pymupdf-layout==1.27.2.3 (page layout analysis; required by the documented commands and for OCR)
  - opencv-python (for OCR support)
- **For OCR**: Tesseract OCR engine
  - macOS: `brew install tesseract`
  - Ubuntu: `sudo apt install tesseract-ocr`

## License

AGPL-3.0 - See [LICENSE](LICENSE) file.

This project uses [pymupdf4llm](https://github.com/pymupdf/pymupdf4llm) which is also AGPL-3.0 licensed.

## Credits

Created by Paul Maunders for use with Claude Code.

## Learn More

- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/agents/skills)
- [PyMuPDF4LLM](https://pypi.org/project/pymupdf4llm/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
