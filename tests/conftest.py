"""
conftest.py
Shared pytest fixtures for Phase 1 tests.
Generates synthetic PDFs in a temp directory instead of relying on disk files.
"""

import os
import pytest
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_pdf(path: str, pages: list) -> None:
    """Write a simple multi-page PDF using reportlab."""
    c = canvas.Canvas(path, pagesize=LETTER)
    _, height = LETTER
    for page_text in pages:
        t = c.beginText(50, height - 50)
        t.setFont("Helvetica", 11)
        for line in page_text.split("\n"):
            t.textLine(line)
        c.drawText(t)
        c.showPage()
    c.save()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def sample_dir(tmp_path_factory):
    """Session-scoped temp directory that holds all synthetic PDFs."""
    return tmp_path_factory.mktemp("samples")


@pytest.fixture(scope="session")
def valid_pdf_path(sample_dir):
    """Two-page synthetic CBC + metabolic panel report."""
    path = str(sample_dir / "valid_report.pdf")
    page1 = (
        "PATIENT LAB REPORT\n"
        "Date: 11/04/2026\n"
        "Lab ID: LAB-0042\n\n"
        "COMPLETE BLOOD COUNT (CBC)\n"
        "Hemoglobin (Hgb):    13.8 g/dL    Reference: 13.5 - 17.5 g/dL\n"
        "Hematocrit (Hct):    41.2 %        Reference: 41 - 53 %\n"
        "RBC Count:           4.70 x10^6/uL   Reference: 4.5 - 5.9 x10^6/uL\n"
        "WBC Count:           7200 cells/uL   Reference: 4500 - 11000 cells/uL\n"
        "Platelet Count:      220000 /uL      Reference: 150000 - 400000 /uL\n"
    )
    page2 = (
        "METABOLIC PANEL\n"
        "Fasting Glucose:   92 mg/dL     Reference: 70 - 99 mg/dL\n"
        "Total Cholesterol: 185 mg/dL    Reference: < 200 mg/dL\n"
        "Creatinine:        0.95 mg/dL   Reference: 0.74 - 1.35 mg/dL\n"
        "Vitamin D (25-OH): 32 ng/mL     Reference: 20 - 50 ng/mL\n"
        "TSH:               2.10 mIU/L   Reference: 0.4 - 4.0 mIU/L\n"
    )
    _write_pdf(path, [page1, page2])
    return path


@pytest.fixture(scope="session")
def multipage_pdf_path(sample_dir):
    """Three-page synthetic report."""
    path = str(sample_dir / "multipage_report.pdf")
    pages = [
        "Lipid Panel\nLDL: 110 mg/dL  Ref: < 130 mg/dL\nHDL: 55 mg/dL   Ref: > 40 mg/dL\n",
        "Thyroid\nTSH: 3.5 mIU/L  Ref: 0.4 - 4.0 mIU/L\nFree T4: 1.1 ng/dL  Ref: 0.8 - 1.8 ng/dL\n",
        "Conclusion\nAll results within normal reference ranges.\n",
    ]
    _write_pdf(path, pages)
    return path


@pytest.fixture(scope="session")
def empty_pdf_path(sample_dir):
    """PDF with one page that has no text content."""
    path = str(sample_dir / "empty_report.pdf")
    c = canvas.Canvas(path, pagesize=LETTER)
    c.showPage()   # blank page, no text drawn
    c.save()
    return path


@pytest.fixture
def non_existent_path(tmp_path):
    """Path that does not exist on disk."""
    return str(tmp_path / "ghost_file.pdf")


@pytest.fixture
def non_pdf_path(tmp_path):
    """A text file with a .txt extension."""
    p = tmp_path / "not_a_pdf.txt"
    p.write_text("This is not a PDF.")
    return str(p)


@pytest.fixture
def corrupted_pdf_path(tmp_path):
    """A file with .pdf extension but invalid content."""
    p = tmp_path / "corrupted.pdf"
    p.write_bytes(b"%PDF-1.4 !! THIS IS NOT VALID PDF CONTENT !!")
    return str(p)
