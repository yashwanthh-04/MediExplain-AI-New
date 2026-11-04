"""
create_samples.py
Generates synthetic medical PDF sample reports for testing.
Run once: python sample_reports/create_samples.py
"""

import os
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def _make_pdf(path: str, pages: list[str]) -> None:
    """Create a multi-page PDF; each string in pages becomes one page."""
    c = canvas.Canvas(path, pagesize=LETTER)
    width, height = LETTER
    for page_text in pages:
        text_obj = c.beginText(50, height - 50)
        text_obj.setFont("Helvetica", 11)
        for line in page_text.split("\n"):
            text_obj.textLine(line)
        c.drawText(text_obj)
        c.showPage()
    c.save()


def create_valid_report(output_dir: str) -> str:
    """Synthetic CBC + metabolic panel report."""
    path = os.path.join(output_dir, "sample_cbc_report.pdf")
    page1 = (
        "PATIENT LAB REPORT\n"
        "Date: 11/04/2026\n"
        "Lab ID: LAB-0042\n\n"
        "COMPLETE BLOOD COUNT (CBC)\n"
        "----------------------------\n"
        "Hemoglobin (Hgb):    13.8 g/dL       Reference: 13.5 - 17.5 g/dL\n"
        "Hematocrit (Hct):    41.2 %           Reference: 41 - 53 %\n"
        "RBC Count:           4.70 x10^6/uL   Reference: 4.5 - 5.9 x10^6/uL\n"
        "WBC Count:           7,200 cells/uL  Reference: 4,500 - 11,000 cells/uL\n"
        "Platelet Count:      220,000 /uL     Reference: 150,000 - 400,000 /uL\n"
    )
    page2 = (
        "METABOLIC PANEL\n"
        "----------------\n"
        "Fasting Glucose:     92 mg/dL         Reference: 70 - 99 mg/dL\n"
        "Total Cholesterol:   185 mg/dL        Reference: < 200 mg/dL (Desirable)\n"
        "Creatinine:          0.95 mg/dL       Reference: 0.74 - 1.35 mg/dL\n"
        "Vitamin D (25-OH):   32 ng/mL         Reference: 20 - 50 ng/mL\n"
        "TSH:                 2.10 mIU/L       Reference: 0.4 - 4.0 mIU/L\n\n"
        "All values within normal range.\n"
        "Reviewed by: Lab Physician\n"
        "Report generated: 11/04/2026\n"
    )
    _make_pdf(path, [page1, page2])
    print(f"Created: {path}")
    return path


def create_multipage_report(output_dir: str) -> str:
    """3-page synthetic report."""
    path = os.path.join(output_dir, "sample_multipage_report.pdf")
    pages = [
        "SYNTHETIC MEDICAL REPORT – PAGE 1\nTest: Lipid Panel\nDate: 2026-11-04\n\nLDL: 110 mg/dL  Reference: < 130 mg/dL\nHDL: 55 mg/dL   Reference: > 40 mg/dL\nTriglycerides: 145 mg/dL  Reference: < 150 mg/dL\n",
        "PAGE 2 – Thyroid Function\nTSH: 3.5 mIU/L   Reference: 0.4 - 4.0 mIU/L\nFree T4: 1.1 ng/dL  Reference: 0.8 - 1.8 ng/dL\nFree T3: 3.2 pg/mL  Reference: 2.3 - 4.2 pg/mL\n",
        "PAGE 3 – Conclusion\nAll results within normal reference ranges.\nFollow-up recommended in 12 months.\n",
    ]
    _make_pdf(path, pages)
    print(f"Created: {path}")
    return path


if __name__ == "__main__":
    out_dir = os.path.dirname(__file__)
    create_valid_report(out_dir)
    create_multipage_report(out_dir)
    print("Sample PDFs created.")
