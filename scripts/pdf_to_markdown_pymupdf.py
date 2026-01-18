#!/usr/bin/env python3
"""
PDF to Markdown converter using PyMuPDF4LLM.

PyMuPDF4LLM is optimised for LLM/RAG workflows, preserving tables, headers,
lists, bold/italic text, and code blocks in GitHub-compatible Markdown.

Usage:
  # Single file
  uv run --with pymupdf4llm --with pymupdf-layout -- python scripts/pdf_to_markdown_pymupdf.py input.pdf

  # Single file with custom output
  uv run --with pymupdf4llm --with pymupdf-layout -- python scripts/pdf_to_markdown_pymupdf.py input.pdf -o output.md

  # Batch process directory
  uv run --with pymupdf4llm --with pymupdf-layout -- python scripts/pdf_to_markdown_pymupdf.py /path/to/pdfs/ -o pymupdf-md/

  # Page chunks (separate markdown per page)
  uv run --with pymupdf4llm --with pymupdf-layout -- python scripts/pdf_to_markdown_pymupdf.py input.pdf --page-chunks

  # OCR for scanned/image-based PDFs (requires Tesseract)
  uv run --with pymupdf4llm --with pymupdf-layout --with opencv-python -- python scripts/pdf_to_markdown_pymupdf.py scanned.pdf --ocr

  # OCR with specific language
  uv run --with pymupdf4llm --with pymupdf-layout --with opencv-python -- python scripts/pdf_to_markdown_pymupdf.py document.pdf --ocr --ocr-language deu

Examples:
  uv run --with pymupdf4llm --with pymupdf-layout -- python scripts/pdf_to_markdown_pymupdf.py "path/to/document.pdf"
  uv run --with pymupdf4llm --with pymupdf-layout -- python scripts/pdf_to_markdown_pymupdf.py /path/to/pdfs/ -o /path/to/output/
"""
import argparse
import sys
from pathlib import Path
import re
import shutil
import subprocess

# IMPORTANT: Import pymupdf.layout BEFORE pymupdf4llm to enable layout mode and OCR support
try:
    import pymupdf.layout  # noqa: F401 - enables layout mode
    LAYOUT_MODE = True
except ImportError:
    LAYOUT_MODE = False

try:
    import pymupdf4llm
except ImportError:
    print("Error: pymupdf4llm package is required.")
    print("Run with: uv run --with pymupdf4llm --with pymupdf-layout -- python ...")
    print("Or install: pip install pymupdf4llm")
    sys.exit(1)


def check_tesseract_available() -> tuple:
    """
    Check if Tesseract OCR is installed and accessible.

    Returns:
        Tuple of (is_available: bool, message: str)
    """
    tesseract_path = shutil.which("tesseract")
    if tesseract_path is None:
        return False, (
            "Tesseract OCR is not installed or not in PATH.\n"
            "Install with:\n"
            "  macOS:   brew install tesseract\n"
            "  Ubuntu:  sudo apt install tesseract-ocr\n"
            "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
        )

    # Get version for informational purposes
    try:
        result = subprocess.run(
            ["tesseract", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        version_line = result.stdout.split('\n')[0] if result.stdout else "unknown version"
        return True, f"Tesseract: {version_line}"
    except Exception:
        return True, f"Tesseract found at: {tesseract_path}"


def clean_table_cell_breaks(text: str) -> str:
    """
    Clean up <br> tags in markdown table cells by replacing them with spaces.
    This merges multi-line content within table cells for better readability.
    """
    # Replace <br> tags (with optional whitespace) with a single space
    text = re.sub(r'<br\s*/?>\s*', ' ', text)
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text


def clean_table_row(line: str) -> str:
    """
    Clean a markdown table row, handling escaped pipes correctly.
    """
    # Split on unescaped pipes only (pipes not preceded by backslash)
    cells = re.split(r'(?<!\\)\|', line)
    cleaned_cells = [clean_table_cell_breaks(cell) for cell in cells]
    return '|'.join(cleaned_cells)


def clean_tables_in_text(text: str) -> str:
    """
    Clean all table rows in the text, removing <br> tags from cells.
    This is always applied regardless of merge settings.
    """
    lines = text.split('\n')
    result = []
    for line in lines:
        if line.strip().startswith('|'):
            result.append(clean_table_row(line))
        else:
            result.append(line)
    return '\n'.join(result)


def merge_paragraph_lines(text: str) -> str:
    """
    Merge lines that are part of the same paragraph.

    Preserves:
    - Headers (lines starting with #)
    - Lists (lines starting with -, *, +, or numbers)
    - Blank lines (paragraph separators)
    - Bold/italic markers at line starts
    - Code blocks (fenced with ```)
    - Table rows (starting with |)

    Merges:
    - Lines that end mid-sentence (no period, ?, !, :)
    - Continuation lines that don't start with special markers
    """
    lines = text.split('\n')
    result = []
    i = 0
    in_code_block = False

    while i < len(lines):
        line = lines[i]

        # Track code block state
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            i += 1
            continue

        # Inside code blocks, preserve everything as-is
        if in_code_block:
            result.append(line)
            i += 1
            continue

        # Keep blank lines as-is
        if not line.strip():
            result.append(line)
            i += 1
            continue

        # Keep table rows as-is (table cleaning is done separately)
        if line.strip().startswith('|'):
            result.append(line)
            i += 1
            continue

        # Keep headers, lists, and special formatting as-is
        if (line.lstrip().startswith('#') or           # Headers
            re.match(r'^\s*[-*+]\s', line) or          # Unordered lists
            re.match(r'^\s*\d+\.\s', line) or          # Ordered lists
            line.strip().startswith('>')):             # Blockquotes
            result.append(line)
            i += 1
            continue

        # Start accumulating a paragraph
        paragraph = line

        # Look ahead to merge continuation lines
        while i + 1 < len(lines):
            next_line = lines[i + 1]

            # Stop at blank lines
            if not next_line.strip():
                break

            # Stop at headers, lists, or special formatting
            if (next_line.lstrip().startswith('#') or
                re.match(r'^\s*[-*+]\s', next_line) or
                re.match(r'^\s*\d+\.\s', next_line) or
                next_line.strip().startswith('```') or
                next_line.strip().startswith('|') or
                next_line.strip().startswith('>')):
                break

            # Check if current line ends mid-sentence
            stripped = paragraph.rstrip()
            # If line ends with sentence-ending punctuation (including after quotes/brackets), don't merge
            if stripped and re.search(r'[.!?:][\'")\]]*$', stripped):
                break

            # Merge the next line with a space
            paragraph = paragraph.rstrip() + ' ' + next_line.lstrip()
            i += 1

        result.append(paragraph)
        i += 1

    return '\n'.join(result)


def convert_pdf_to_markdown(
    pdf_path: Path,
    output_path: Path = None,
    page_chunks: bool = False,
    merge_lines: bool = True,
    use_ocr: bool = False,
    ocr_language: str = "eng",
    ocr_dpi: int = 400
) -> bool:
    """Convert a single PDF to Markdown. Returns True on success, False on failure."""
    try:
        ocr_indicator = " [OCR]" if use_ocr else ""
        print(f"Converting {pdf_path.name}{ocr_indicator}...", end=" ")

        if page_chunks:
            # Get list of dicts, one per page
            md_data = pymupdf4llm.to_markdown(
                str(pdf_path),
                page_chunks=True,
                use_ocr=use_ocr,
                ocr_language=ocr_language,
                ocr_dpi=ocr_dpi
            )

            # Default output: replace .pdf with _page_N.md
            if output_path is None:
                output_base = pdf_path.with_suffix('')
                for i, page_data in enumerate(md_data, start=1):
                    page_text = page_data['text']
                    # Always clean tables, optionally merge paragraphs
                    page_text = clean_tables_in_text(page_text)
                    if merge_lines:
                        page_text = merge_paragraph_lines(page_text)
                    page_output = output_base.parent / f"{output_base.name}_page_{i}.md"
                    page_output.write_text(page_text, encoding='utf-8')
                print(f"✓ Created {len(md_data)} page files")
                return True
            else:
                # If output is a directory, create page files there
                if output_path.is_dir() or not output_path.suffix:
                    output_path.mkdir(parents=True, exist_ok=True)
                    output_base = output_path / pdf_path.stem
                    for i, page_data in enumerate(md_data, start=1):
                        page_text = page_data['text']
                        # Always clean tables, optionally merge paragraphs
                        page_text = clean_tables_in_text(page_text)
                        if merge_lines:
                            page_text = merge_paragraph_lines(page_text)
                        page_output = output_path / f"{pdf_path.stem}_page_{i}.md"
                        page_output.write_text(page_text, encoding='utf-8')
                    print(f"✓ Created {len(md_data)} page files in {output_path}")
                    return True
                else:
                    print(f"✗ Error: page_chunks requires output to be a directory")
                    return False
        else:
            # Single markdown file
            md_text = pymupdf4llm.to_markdown(
                str(pdf_path),
                use_ocr=use_ocr,
                ocr_language=ocr_language,
                ocr_dpi=ocr_dpi
            )

            # Always clean tables, optionally merge paragraphs
            md_text = clean_tables_in_text(md_text)
            if merge_lines:
                md_text = merge_paragraph_lines(md_text)

            # Determine output path
            if output_path is None:
                output_path = pdf_path.with_suffix('.md')
            elif output_path.is_dir() or str(output_path).endswith('/') or not output_path.suffix:
                # Treat as directory if: exists as dir, ends with /, or has no extension
                output_path = Path(output_path) / pdf_path.with_suffix('.md').name

            # Write markdown
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(md_text, encoding='utf-8')

            # Show file size
            size_kb = len(md_text) / 1024
            print(f"✓ {size_kb:.1f}KB → {output_path.name}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF(s) to Markdown using PyMuPDF4LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "input",
        type=Path,
        help="PDF file or directory containing PDFs"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file or directory (default: same location as input with .md extension)"
    )
    parser.add_argument(
        "--page-chunks",
        action="store_true",
        help="Generate separate markdown file per page"
    )
    parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Don't merge paragraph lines (keep original line breaks from PDF)"
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Enable OCR for scanned/image-based pages (requires Tesseract)"
    )
    parser.add_argument(
        "--ocr-language",
        type=str,
        default="eng",
        help="Tesseract language code(s), e.g., 'eng', 'eng+deu' (default: eng)"
    )
    parser.add_argument(
        "--ocr-dpi",
        type=int,
        default=400,
        help="OCR resolution in DPI (default: 400, higher=more accurate but slower)"
    )

    args = parser.parse_args()

    # Check Tesseract and OpenCV if OCR is requested
    if args.ocr:
        if not LAYOUT_MODE:
            print("Error: OCR requires pymupdf-layout package.")
            print("Install with: pip install pymupdf-layout")
            sys.exit(1)
        # Check OpenCV is available
        try:
            import cv2  # noqa: F401
        except ImportError:
            print("Error: OCR requires opencv-python package.")
            print("Add --with opencv-python to your uv run command:")
            print("  uv run --with pymupdf4llm --with pymupdf-layout --with opencv-python -- python ...")
            sys.exit(1)
        tesseract_ok, tesseract_msg = check_tesseract_available()
        if not tesseract_ok:
            print(f"Error: {tesseract_msg}")
            sys.exit(1)
        print(f"OCR enabled ({tesseract_msg})")
        print(f"  Language: {args.ocr_language}, DPI: {args.ocr_dpi}")
        print()

    merge_lines = not args.no_merge

    # Handle single file
    if args.input.is_file():
        if args.input.suffix.lower() != '.pdf':
            print(f"Error: {args.input} is not a PDF file")
            sys.exit(1)
        success = convert_pdf_to_markdown(
            args.input, args.output, args.page_chunks, merge_lines,
            args.ocr, args.ocr_language, args.ocr_dpi
        )
        if not success:
            sys.exit(1)

    # Handle directory
    elif args.input.is_dir():
        pdf_files = list(args.input.glob("*.pdf"))

        if not pdf_files:
            print(f"No PDF files found in {args.input}")
            sys.exit(1)

        print(f"Found {len(pdf_files)} PDF file(s)")

        # Create output directory if specified
        output_dir = args.output
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        # Convert each PDF, track failures
        failures = 0
        for pdf_file in sorted(pdf_files):
            success = convert_pdf_to_markdown(
                pdf_file, output_dir, args.page_chunks, merge_lines,
                args.ocr, args.ocr_language, args.ocr_dpi
            )
            if not success:
                failures += 1

        if failures > 0:
            print(f"\n{failures} file(s) failed to convert")
            sys.exit(1)

    else:
        print(f"Error: {args.input} does not exist")
        sys.exit(1)


if __name__ == "__main__":
    main()
