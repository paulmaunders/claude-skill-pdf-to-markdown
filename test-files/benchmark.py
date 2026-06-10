#!/usr/bin/env python3
"""
Benchmark PyMuPDF4LLM PDF conversion performance.

Usage:
    uv run --with pymupdf4llm==0.3.4 -- python test-files/benchmark.py test-files/large-document.pdf
"""

import sys
import time
from pathlib import Path


def benchmark_pymupdf(pdf_path: Path):
    """Benchmark PyMuPDF4LLM conversion."""
    import pymupdf4llm

    print(f"Benchmarking PyMuPDF4LLM on {pdf_path.name}...")

    start_time = time.time()
    md_text = pymupdf4llm.to_markdown(str(pdf_path))
    end_time = time.time()

    elapsed = end_time - start_time
    size_kb = len(md_text) / 1024

    print(f"\nResults:")
    print(f"  Time: {elapsed:.2f} seconds")
    print(f"  Output size: {size_kb:.1f} KB")
    print(f"  Speed: {len(md_text) / elapsed / 1024:.1f} KB/sec")

    return elapsed, size_kb


def main():
    if len(sys.argv) < 2:
        print("Usage: python benchmark.py <pdf_file>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])

    if not pdf_path.exists():
        print(f"Error: {pdf_path} does not exist")
        sys.exit(1)

    print(f"PDF: {pdf_path}")
    print(f"Size: {pdf_path.stat().st_size / 1024:.1f} KB\n")

    benchmark_pymupdf(pdf_path)


if __name__ == "__main__":
    main()
