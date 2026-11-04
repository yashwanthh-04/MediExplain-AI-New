# MediExplain AI – Phase 1: Medical Document Processing

## Overview

Phase 1 provides the document ingestion pipeline for MediExplain AI.  
It accepts medical PDF reports, extracts and cleans the text, splits it into
overlapping chunks, and exposes a small educational medical knowledge base.

Phase 2 consumes the output of this phase without modifying it.

---

## Project Structure

```
MediExplain-AI/
├── document_processing/
│   ├── __init__.py           # Exposes process_medical_pdf, get_document_chunks
│   ├── pdf_extractor.py      # PDF validation + PyMuPDF text extraction
│   ├── text_cleaner.py       # Whitespace cleanup, medical value preservation
│   ├── chunking.py           # Overlapping semantic chunking with metadata
│   └── document_processor.py # Integration interface (the two canonical functions)
├── medical_knowledge/
│   ├── __init__.py
│   ├── medical_glossary.json # Educational glossary (10 terms, MedlinePlus sourced)
│   └── glossary_loader.py    # load_glossary / get_term / list_terms
├── sample_reports/
│   ├── create_samples.py           # Script to regenerate synthetic PDFs
│   ├── sample_cbc_report.pdf       # 2-page synthetic CBC + metabolic panel
│   └── sample_multipage_report.pdf # 3-page synthetic report
├── tests/
│   ├── conftest.py              # Shared pytest fixtures (synthetic PDFs)
│   ├── test_pdf_extractor.py    # PDF validation & extraction tests
│   ├── test_text_cleaner.py     # Text cleaning & value preservation tests
│   ├── test_chunking.py         # Chunking & metadata tests
│   ├── test_glossary.py         # Glossary loader tests
│   └── test_integration.py      # End-to-end integration tests
├── requirements.txt
└── README_PHASE1.md
```

---

## Installation

```bash
pip install -r requirements.txt
```

Dependencies: `PyMuPDF`, `pytest`, `pytest-cov`, `reportlab`

---

## Usage

### Process a PDF

```python
from document_processing.document_processor import process_medical_pdf, get_document_chunks

# Step 1 – extract and clean
doc = process_medical_pdf("path/to/report.pdf")

# Step 2 – chunk for retrieval
chunks = get_document_chunks(doc)
```

### Query the glossary

```python
from medical_knowledge.glossary_loader import get_term, list_terms

print(list_terms())          # all 10 term keys
print(get_term("hemoglobin"))
```

---

## Integration Functions

### `process_medical_pdf(file_path) -> dict`

Returns:

```python
{
  "document_id":        str,        # unique UUID
  "file_path":          str,
  "filename":           str,
  "total_pages":        int,
  "pages": [
    {
      "page_number":     int,        # 1-based
      "raw_text":        str,
      "cleaned_text":    str,
      "char_count":      int,
      "is_empty":        bool,
      "extraction_note": str         # "ok" | "empty page" | "possible scan"
    }
  ],
  "full_raw_text":      str,
  "full_cleaned_text":  str,
  "warnings":           [str],
  "status":             "success" | "error",
  "error_message":      str | None
}
```

### `get_document_chunks(processed_document, chunk_size=500, chunk_overlap=100) -> list`

Returns a flat list of chunk dicts:

```python
{
  "chunk_id":      str,   # UUID per chunk
  "document_id":  str,   # matches processed_document["document_id"]
  "filename":     str,
  "page_number":  int,
  "chunk_index":  int,   # 0-based within the page
  "text":         str,
  "char_count":   int,
  "start_char":   int,   # offset in cleaned page text
  "end_char":     int
}
```

---

## Output Contract for Phase 2

Phase 2 should expect:

- `process_medical_pdf` always returns a dict (never raises on bad input).
  Check `result["status"]` before proceeding.
- `get_document_chunks` always returns a list (empty on error/empty PDF).
- Every chunk carries `document_id`, `filename`, `page_number`, and `chunk_index`
  so Phase 2 can reconstruct provenance for any retrieved passage.
- Medical numbers, units, dates, and reference ranges are guaranteed to be
  unchanged from the source PDF.

---

## Running Tests

```bash
python -m pytest tests/ -v
```

103 tests, 0 failures.

---

## Notes

- All sample reports use synthetic data. No real patient information is included.
- Reference ranges in the glossary are sourced from MedlinePlus and are for
  educational purposes only — not clinical use.
