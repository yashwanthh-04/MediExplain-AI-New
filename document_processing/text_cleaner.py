"""
text_cleaner.py
Cleans extracted PDF text while preserving all medical values,
units, reference ranges, dates, and terminology.
"""

import re


def clean_medical_text(raw_text: str) -> str:
    """
    Clean raw extracted text for downstream processing.

    Rules:
    - Remove form-feed characters and null bytes
    - Normalise line endings to \\n
    - Collapse runs of blank lines (keep at most one blank line)
    - Remove leading/trailing whitespace from each line
    - Collapse multiple spaces on a single line to one space
      BUT do NOT touch numbers, units, decimal points, slashes, or dashes
      that are part of medical values (e.g. "12.5 g/dL", "4.5-5.5", "03/15/2024")
    - Strip leading/trailing whitespace from the full result

    Intentionally NOT changed:
    - Numbers and decimals  (e.g. 4.5, 0.9)
    - Units                 (e.g. g/dL, mmol/L, mg/dL, 10^3/µL)
    - Reference ranges      (e.g. 4.5-5.5, 70-100)
    - Dates                 (e.g. 03/15/2024, 2024-03-15)
    - Test names and medical terms
    """
    if not raw_text:
        return ""

    text = raw_text

    # Remove null bytes and form-feed characters
    text = text.replace("\x00", "").replace("\f", "\n")

    # Normalise Windows/Mac line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing whitespace on every line, keep internal spacing intact
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        # Strip only leading/trailing whitespace per line
        stripped = line.strip()
        # Collapse multiple internal spaces to a single space
        # Use a non-greedy approach that won't affect value patterns
        stripped = re.sub(r" {2,}", " ", stripped)
        cleaned_lines.append(stripped)

    # Collapse consecutive blank lines to a single blank line
    result_lines = []
    prev_blank = False
    for line in cleaned_lines:
        is_blank = line == ""
        if is_blank and prev_blank:
            continue  # skip redundant blank lines
        result_lines.append(line)
        prev_blank = is_blank

    return "\n".join(result_lines).strip()
