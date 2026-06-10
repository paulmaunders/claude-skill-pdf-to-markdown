#!/usr/bin/env python3
"""
Generate an image-only (scanned-style) PDF for testing OCR.

The page is rendered to a raster image and embedded, so the PDF has NO text
layer. Standard extraction yields nothing; only OCR can recover the text.

Usage:
    uv run --with pymupdf==1.27.2.3 -- python test-files/generate_scanned_pdf.py
"""
import sys
from pathlib import Path

import pymupdf

# Lines rendered onto the page. Tests assert these come back via OCR.
LINES = [
    ("Scanned Document Test", 22),
    ("This page has no text layer.", 14),
    ("OCR must extract these words.", 14),
    ("Invoice Number: 12345", 14),
]


def create_scanned_pdf(output_path: Path) -> None:
    width, height = 595, 842  # A4 in points

    # Draw the text on a temporary page, rasterise it, then embed as an image
    # on the output page so the result has no extractable text layer.
    tmp = pymupdf.open()
    tmp_page = tmp.new_page(width=width, height=height)
    y = 100
    for text, size in LINES:
        tmp_page.insert_text((72, y), text, fontsize=size)
        y += size * 2
    # Grayscale at a modest DPI keeps the committed fixture small while
    # remaining legible to Tesseract.
    pixmap = tmp_page.get_pixmap(dpi=120, colorspace=pymupdf.csGRAY)
    png_bytes = pixmap.tobytes("png")

    doc = pymupdf.open()
    page = doc.new_page(width=width, height=height)
    page.insert_image(pymupdf.Rect(0, 0, width, height), stream=png_bytes)
    doc.save(str(output_path), garbage=4, deflate=True, deflate_images=True)

    text_chars = len(page.get_text().strip())
    print(f"✓ Generated: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"  Text-layer characters: {text_chars} (expected 0)")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "scanned-document.pdf"
    create_scanned_pdf(out)
