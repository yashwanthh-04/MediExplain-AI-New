"""
document_processor.py
Integration interface for Phase 1.
Exposes two canonical functions consumed by Phase 2.
"""

import uuid
from document_processing.pdf_extractor import extract_text_from_pdf, PDFExtractionError
from document_processing.text_cleaner import clean_medical_text
from document_processing.chunking import chunk_document, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


def process_medical_pdf(file_path: str) -> dict:
    """
    Full pipeline: validate → extract → clean → attach document ID.

    Args:
        file_path: Absolute or relative path to a PDF file.

    Returns a structured document dict:
    {
        "document_id":   str,        # unique UUID for this document
        "file_path":     str,
        "filename":      str,
        "total_pages":   int,
        "pages": [
            {
                "page_number":      int,
                "raw_text":         str,
                "cleaned_text":     str,
                "char_count":       int,
                "is_empty":         bool,
                "extraction_note":  str
            },
            ...
        ],
        "full_raw_text":     str,
        "full_cleaned_text": str,
        "warnings":          [str],
        "status":            "success" | "error",
        "error_message":     str | None
    }

    Raises:
        PDFExtractionError: if the file is invalid or unreadable.
    """
    try:
        extraction = extract_text_from_pdf(file_path)
    except PDFExtractionError as e:
        return {
            "document_id": None,
            "file_path": file_path,
            "filename": "",
            "total_pages": 0,
            "pages": [],
            "full_raw_text": "",
            "full_cleaned_text": "",
            "warnings": [],
            "status": "error",
            "error_message": str(e),
        }

    document_id = str(uuid.uuid4())
    extraction["document_id"] = document_id

    processed_pages = []
    cleaned_parts = []

    for page in extraction["pages"]:
        cleaned = clean_medical_text(page["text"])
        processed_pages.append({
            "page_number": page["page_number"],
            "raw_text": page["text"],
            "cleaned_text": cleaned,
            "char_count": page["char_count"],
            "is_empty": page["is_empty"],
            "extraction_note": page["extraction_note"],
        })
        if cleaned.strip():
            cleaned_parts.append(cleaned)

    return {
        "document_id": document_id,
        "file_path": extraction["file_path"],
        "filename": extraction["filename"],
        "total_pages": extraction["total_pages"],
        "pages": processed_pages,
        "full_raw_text": extraction["full_text"],
        "full_cleaned_text": "\n".join(cleaned_parts),
        "warnings": extraction["warnings"],
        "status": "success",
        "error_message": None,
        # carry the internal key so chunking can use it
        "_extraction": extraction,
    }


def get_document_chunks(
    processed_document: dict,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list:
    """
    Generate overlapping semantic chunks from a processed document.

    Args:
        processed_document: Output from process_medical_pdf().
        chunk_size:         Characters per chunk (default 500).
        chunk_overlap:      Overlap characters (default 100).

    Returns:
        List of chunk dicts (see chunking.chunk_text for schema).
        Returns an empty list if the document had an error or no text.
    """
    if processed_document.get("status") == "error":
        return []

    # Build an extraction-compatible dict for chunk_document
    extraction_compat = {
        "document_id": processed_document["document_id"],
        "filename": processed_document["filename"],
        "pages": [
            {
                "page_number": p["page_number"],
                "text": p["raw_text"],   # chunking module will re-clean
                "is_empty": p["is_empty"],
            }
            for p in processed_document["pages"]
        ],
    }

    return chunk_document(
        extraction_result=extraction_compat,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
