"""
pdf_extractor.py
Handles PDF validation and text extraction using PyMuPDF (fitz).
"""

import os
import fitz  # PyMuPDF

MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSION = ".pdf"


class PDFExtractionError(Exception):
    """Raised when PDF extraction fails."""
    pass


def validate_pdf(file_path: str) -> dict:
    """
    Validate a PDF file before extraction.

    Checks:
    - File exists
    - Correct .pdf extension
    - File size within limit
    - File is a readable PDF (not corrupted)

    Returns a dict with 'valid' (bool) and 'reason' (str).
    """
    if not os.path.exists(file_path):
        return {"valid": False, "reason": f"File not found: {file_path}"}

    ext = os.path.splitext(file_path)[1].lower()
    if ext != ALLOWED_EXTENSION:
        return {"valid": False, "reason": f"Invalid file type '{ext}'. Only .pdf is accepted."}

    size = os.path.getsize(file_path)
    if size == 0:
        return {"valid": False, "reason": "File is empty (0 bytes)."}
    if size > MAX_FILE_SIZE_BYTES:
        return {
            "valid": False,
            "reason": f"File size {size / (1024*1024):.1f} MB exceeds {MAX_FILE_SIZE_MB} MB limit."
        }

    # Try opening to catch corrupted files
    try:
        doc = fitz.open(file_path)
        doc.close()
    except Exception as e:
        return {"valid": False, "reason": f"Cannot open PDF (possibly corrupted): {e}"}

    return {"valid": True, "reason": "OK"}


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extract text from a PDF file page by page.

    Returns a dict:
    {
        "file_path": str,
        "filename": str,
        "total_pages": int,
        "pages": [
            {
                "page_number": int,       # 1-based
                "text": str,
                "char_count": int,
                "is_empty": bool,
                "extraction_note": str    # e.g. "ok", "empty page", "possible scan"
            },
            ...
        ],
        "full_text": str,
        "warnings": [str]
    }
    """
    validation = validate_pdf(file_path)
    if not validation["valid"]:
        raise PDFExtractionError(validation["reason"])

    filename = os.path.basename(file_path)
    result = {
        "file_path": file_path,
        "filename": filename,
        "total_pages": 0,
        "pages": [],
        "full_text": "",
        "warnings": []
    }

    try:
        doc = fitz.open(file_path)
        result["total_pages"] = len(doc)

        if len(doc) == 0:
            result["warnings"].append("PDF has zero pages.")
            doc.close()
            return result

        all_text_parts = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")  # plain text extraction

            char_count = len(text.strip())
            is_empty = char_count == 0

            if is_empty:
                # Check if the page has images (possible scan)
                image_list = page.get_images(full=False)
                if image_list:
                    note = "possible scan – image-only page, no extractable text"
                    result["warnings"].append(
                        f"Page {page_num + 1}: {note}"
                    )
                else:
                    note = "empty page"
            else:
                note = "ok"

            page_data = {
                "page_number": page_num + 1,
                "text": text,
                "char_count": char_count,
                "is_empty": is_empty,
                "extraction_note": note
            }
            result["pages"].append(page_data)

            if not is_empty:
                all_text_parts.append(text)

        result["full_text"] = "\n".join(all_text_parts)
        doc.close()

    except PDFExtractionError:
        raise
    except Exception as e:
        raise PDFExtractionError(f"Unexpected error during extraction: {e}")

    if not result["full_text"].strip():
        result["warnings"].append(
            "No text was extracted. The PDF may be scanned or image-based."
        )

    return result
