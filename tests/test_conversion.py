#!/usr/bin/env python3
"""
Integration tests for PDF to Markdown conversion.

Run with:
    uv run --with pymupdf4llm --with pymupdf-layout --with pytest -- pytest tests/
"""

import subprocess
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "pdf_to_markdown_pymupdf.py"
TEST_FILES = PROJECT_ROOT / "test-files"


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
