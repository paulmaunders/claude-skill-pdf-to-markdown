#!/usr/bin/env python3
"""
Integration tests for PDF to Markdown conversion.

Run with:
    uv run --with pymupdf4llm==0.3.4 --with pymupdf-layout==1.27.2.3 --with pytest -- pytest tests/
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "pdf_to_markdown_pymupdf.py"
TEST_FILES = PROJECT_ROOT / "test-files"


def ocr_available() -> bool:
    """True only when both OpenCV and Tesseract are installed for real OCR runs."""
    if shutil.which("tesseract") is None:
        return False
    try:
        import cv2  # noqa: F401
    except ImportError:
        return False
    return True


def run_conversion(pdf_path: Path, extra_args: list = None) -> tuple[str, str, int]:
    """Run the conversion script and return stdout, stderr, and return code."""
    cmd = [sys.executable, str(SCRIPT_PATH), str(pdf_path)]
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


class TestSampleDocumentConversion:
    """Test conversion of the sample document."""

    def test_converts_successfully(self, tmp_path):
        """Test that sample-document.pdf converts without errors."""
        pdf_path = TEST_FILES / "sample-document.pdf"
        output_path = tmp_path / "output.md"

        stdout, stderr, returncode = run_conversion(pdf_path, ["-o", str(output_path)])

        assert returncode == 0, f"Conversion failed: {stderr}"
        assert output_path.exists(), "Output file was not created"
        assert output_path.stat().st_size > 0, "Output file is empty"

    def test_output_contains_headers(self, tmp_path):
        """Test that headers are preserved in output."""
        pdf_path = TEST_FILES / "sample-document.pdf"
        output_path = tmp_path / "output.md"

        run_conversion(pdf_path, ["-o", str(output_path)])
        content = output_path.read_text()

        # Check for markdown headers
        assert "## " in content or "# " in content, "No headers found in output"

    def test_header_hierarchy_preserved(self, tmp_path):
        """Multi-level headers must keep their levels (H1/H2/H3), not flatten to ##.

        Guards against the ML layout engine taking over the non-OCR path:
        pymupdf4llm 1.27.x+ flattens every heading to '##'.
        """
        pdf_path = TEST_FILES / "sample-document.pdf"
        output_path = tmp_path / "output.md"

        run_conversion(pdf_path, ["-o", str(output_path)])
        lines = output_path.read_text().split("\n")

        h1 = [l for l in lines if l.startswith("# ")]
        h2 = [l for l in lines if l.startswith("## ")]
        h3 = [l for l in lines if l.startswith("### ")]

        assert h1, "No H1 headers found - hierarchy may have been flattened"
        assert h2, "No H2 headers found"
        assert h3, "No H3 headers found - hierarchy may have been flattened"

    def test_output_contains_tables(self, tmp_path):
        """Test that tables are preserved in output."""
        pdf_path = TEST_FILES / "sample-document.pdf"
        output_path = tmp_path / "output.md"

        run_conversion(pdf_path, ["-o", str(output_path)])
        content = output_path.read_text()

        # Check for markdown table syntax
        assert "|" in content, "No tables found in output"
        assert "---" in content, "No table separators found in output"

    def test_output_contains_lists(self, tmp_path):
        """Test that lists are preserved in output."""
        pdf_path = TEST_FILES / "sample-document.pdf"
        output_path = tmp_path / "output.md"

        run_conversion(pdf_path, ["-o", str(output_path)])
        content = output_path.read_text()

        # Check for list markers
        assert "- " in content, "No unordered lists found in output"

    def test_table_cells_cleaned(self, tmp_path):
        """Test that <br> tags are removed from table cells."""
        pdf_path = TEST_FILES / "sample-document.pdf"
        output_path = tmp_path / "output.md"

        run_conversion(pdf_path, ["-o", str(output_path)])
        content = output_path.read_text()

        # Check that <br> tags are removed
        assert "<br>" not in content, "Found unprocessed <br> tags in output"
        assert "<br/>" not in content, "Found unprocessed <br/> tags in output"


class TestLargeDocumentConversion:
    """Test conversion of the large document."""

    def test_converts_successfully(self, tmp_path):
        """Test that large-document.pdf converts without errors."""
        pdf_path = TEST_FILES / "large-document.pdf"
        output_path = tmp_path / "output.md"

        stdout, stderr, returncode = run_conversion(pdf_path, ["-o", str(output_path)])

        assert returncode == 0, f"Conversion failed: {stderr}"
        assert output_path.exists(), "Output file was not created"

    def test_output_is_substantial(self, tmp_path):
        """Test that output contains substantial content from multi-page PDF."""
        pdf_path = TEST_FILES / "large-document.pdf"
        output_path = tmp_path / "output.md"

        run_conversion(pdf_path, ["-o", str(output_path)])
        content = output_path.read_text()

        # Large document should produce substantial output
        assert len(content) > 10000, "Output seems too small for a 35-page document"


class TestCommandLineOptions:
    """Test command-line options."""

    def test_no_merge_option(self, tmp_path):
        """Test that --no-merge preserves original line breaks."""
        pdf_path = TEST_FILES / "sample-document.pdf"
        output_merged = tmp_path / "merged.md"
        output_unmerged = tmp_path / "unmerged.md"

        run_conversion(pdf_path, ["-o", str(output_merged)])
        run_conversion(pdf_path, ["-o", str(output_unmerged), "--no-merge"])

        merged_content = output_merged.read_text()
        unmerged_content = output_unmerged.read_text()

        # Unmerged should have more lines
        merged_lines = len(merged_content.splitlines())
        unmerged_lines = len(unmerged_content.splitlines())

        assert unmerged_lines >= merged_lines, "--no-merge should preserve more line breaks"

    def test_page_chunks_option(self, tmp_path):
        """Test that --page-chunks creates separate files per page."""
        pdf_path = TEST_FILES / "sample-document.pdf"
        output_dir = tmp_path / "pages"
        output_dir.mkdir()

        stdout, stderr, returncode = run_conversion(
            pdf_path,
            ["-o", str(output_dir), "--page-chunks"]
        )

        assert returncode == 0, f"Conversion failed: {stderr}"

        # Should create multiple page files
        page_files = list(output_dir.glob("*_page_*.md"))
        assert len(page_files) >= 2, "Expected multiple page files for multi-page PDF"

    def test_invalid_file_error(self):
        """Test that non-existent file produces error."""
        stdout, stderr, returncode = run_conversion(Path("/nonexistent/file.pdf"))

        assert returncode != 0, "Should fail for non-existent file"

    def test_non_pdf_error(self, tmp_path):
        """Test that non-PDF file produces error."""
        fake_pdf = tmp_path / "fake.txt"
        fake_pdf.write_text("not a pdf")

        stdout, stderr, returncode = run_conversion(fake_pdf)

        assert returncode != 0, "Should fail for non-PDF file"


class TestOCRRequirements:
    """Test OCR-related error handling."""

    def test_ocr_flag_handled(self, tmp_path):
        """Test that --ocr flag is handled correctly."""
        pdf_path = TEST_FILES / "sample-document.pdf"
        output_path = tmp_path / "output.md"

        stdout, stderr, returncode = run_conversion(
            pdf_path, ["-o", str(output_path), "--ocr"]
        )

        # Either OCR works (opencv + tesseract installed) or we get a helpful error
        if returncode != 0:
            combined_output = (stdout + stderr).lower()
            # Should mention one of the missing requirements
            has_helpful_error = (
                "opencv" in combined_output or
                "tesseract" in combined_output or
                "pymupdf-layout" in combined_output
            )
            assert has_helpful_error, f"Expected helpful error message, got: {stdout}{stderr}"
        else:
            # OCR succeeded, output should exist
            assert output_path.exists(), "Output file should exist when OCR succeeds"


class TestOCRExtraction:
    """End-to-end OCR on an image-only PDF (skipped if OCR deps are missing)."""

    def test_scanned_pdf_has_no_text_layer(self, tmp_path):
        """Without OCR, the scanned fixture yields effectively no text."""
        pdf_path = TEST_FILES / "scanned-document.pdf"
        output_path = tmp_path / "no_ocr.md"

        run_conversion(pdf_path, ["-o", str(output_path)])

        # Image-only PDF: standard extraction should produce little/no text
        assert "Invoice Number" not in output_path.read_text()

    @pytest.mark.skipif(not ocr_available(), reason="Requires Tesseract and OpenCV")
    def test_ocr_recovers_text_from_scan(self, tmp_path):
        """With OCR, the embedded text is recovered from the image-only PDF."""
        pdf_path = TEST_FILES / "scanned-document.pdf"
        output_path = tmp_path / "ocr.md"

        stdout, stderr, returncode = run_conversion(
            pdf_path, ["-o", str(output_path), "--ocr"]
        )

        assert returncode == 0, f"OCR conversion failed: {stdout}{stderr}"
        content = output_path.read_text()
        assert "Scanned Document Test" in content, f"OCR missed the title: {content!r}"
        assert "Invoice Number: 12345" in content, f"OCR missed the body: {content!r}"


class TestOutputCleanliness:
    """Guard against formatting regressions in the post-processing."""

    def test_no_trailing_whitespace(self, tmp_path):
        """Output lines should be trimmed (PyMuPDF4LLM emits trailing spaces)."""
        pdf_path = TEST_FILES / "sample-document.pdf"
        output_path = tmp_path / "output.md"

        run_conversion(pdf_path, ["-o", str(output_path)])

        lines_with_trailing = [
            line for line in output_path.read_text().split("\n") if line != line.rstrip()
        ]
        assert not lines_with_trailing, f"Found trailing whitespace on lines: {lines_with_trailing!r}"
