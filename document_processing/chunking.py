"""
chunking.py
Splits cleaned medical text into overlapping chunks with metadata.
"""

import uuid
from typing import List, Dict, Any


DEFAULT_CHUNK_SIZE = 500    # characters
DEFAULT_CHUNK_OVERLAP = 100  # characters


def chunk_text(
    text: str,
    document_id: str,
    filename: str,
    page_number: int = 1,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Split a block of text into overlapping chunks.

    Each chunk carries metadata so Phase 2 can trace it back to its source.

    Args:
        text:          Cleaned text to split.
        document_id:   Unique ID for the parent document.
        filename:      Original filename (for metadata).
        page_number:   Page this text came from (1-based).
        chunk_size:    Max characters per chunk.
        chunk_overlap: Characters of overlap between consecutive chunks.

    Returns:
        List of chunk dicts:
        {
            "chunk_id":      str,   # unique UUID per chunk
            "document_id":  str,
            "filename":     str,
            "page_number":  int,
            "chunk_index":  int,   # 0-based index within this page
            "text":         str,
            "char_count":   int,
            "start_char":   int,   # offset in the original text
            "end_char":     int
        }
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be non-negative.")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    if not text or not text.strip():
        return []

    chunks = []
    start = 0
    chunk_index = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk_text_content = text[start:end]

        # Avoid chunks that are only whitespace
        if chunk_text_content.strip():
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "document_id": document_id,
                "filename": filename,
                "page_number": page_number,
                "chunk_index": chunk_index,
                "text": chunk_text_content,
                "char_count": len(chunk_text_content),
                "start_char": start,
                "end_char": min(end, text_length),
            })
            chunk_index += 1

        # Move forward by (chunk_size - overlap)
        step = chunk_size - chunk_overlap
        start += step

    return chunks


def chunk_document(
    extraction_result: dict,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Chunk every page of an extraction result produced by pdf_extractor.

    Args:
        extraction_result: Output from extract_text_from_pdf().
        chunk_size:        Characters per chunk.
        chunk_overlap:     Overlap between consecutive chunks.

    Returns:
        Flat list of all chunk dicts across all pages.
    """
    all_chunks: List[Dict[str, Any]] = []
    document_id = extraction_result.get("document_id", str(uuid.uuid4()))
    filename = extraction_result.get("filename", "unknown.pdf")

    for page in extraction_result.get("pages", []):
        if page["is_empty"]:
            continue

        from document_processing.text_cleaner import clean_medical_text
        clean_text = clean_medical_text(page["text"])

        page_chunks = chunk_text(
            text=clean_text,
            document_id=document_id,
            filename=filename,
            page_number=page["page_number"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        all_chunks.extend(page_chunks)

    return all_chunks
