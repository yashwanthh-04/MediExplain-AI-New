"""
test_integration.py
End-to-end tests for the two Phase 1 integration functions:
  - process_medical_pdf()
  - get_document_chunks()
"""

import pytest
from document_processing.document_processor import process_medical_pdf, get_document_chunks


class TestProcessMedicalPdf:
    def test_returns_dict(self, valid_pdf_path):
        result = process_medical_pdf(valid_pdf_path)
        assert isinstance(result, dict)

    def test_status_success_on_valid_pdf(self, valid_pdf_path):
        result = process_medical_pdf(valid_pdf_path)
        assert result["status"] == "success"

    def test_error_message_none_on_success(self, valid_pdf_path):
        result = process_medical_pdf(valid_pdf_path)
        assert result["error_message"] is None

    def test_document_id_assigned(self, valid_pdf_path):
        result = process_medical_pdf(valid_pdf_path)
        assert result["document_id"] is not None
        assert len(result["document_id"]) > 0

    def test_filename_matches(self, valid_pdf_path):
        result = process_medical_pdf(valid_pdf_path)
        assert result["filename"] == "valid_report.pdf"

    def test_total_pages_correct(self, valid_pdf_path):
        result = process_medical_pdf(valid_pdf_path)
        assert result["total_pages"] == 2

    def test_pages_list_populated(self, valid_pdf_path):
        result = process_medical_pdf(valid_pdf_path)
        assert len(result["pages"]) == 2

    def test_page_has_raw_and_cleaned_text(self, valid_pdf_path):
        result = process_medical_pdf(valid_pdf_path)
        for page in result["pages"]:
            assert "raw_text" in page
            assert "cleaned_text" in page

    def test_full_cleaned_text_not_empty(self, valid_pdf_path):
        result = process_medical_pdf(valid_pdf_path)
        assert result["full_cleaned_text"].strip() != ""

    def test_medical_values_in_cleaned_text(self, valid_pdf_path):
        result = process_medical_pdf(valid_pdf_path)
        text = result["full_cleaned_text"]
        assert "13.8" in text      # Hemoglobin value
        assert "g/dL" in text      # unit
        assert "92" in text        # Glucose value
        assert "mg/dL" in text     # unit
        assert "2.10" in text      # TSH value

    def test_status_error_on_invalid_path(self, non_existent_path):
        result = process_medical_pdf(non_existent_path)
        assert result["status"] == "error"
        assert result["error_message"] is not None

    def test_status_error_on_corrupted_pdf(self, corrupted_pdf_path):
        result = process_medical_pdf(corrupted_pdf_path)
        assert result["status"] == "error"

    def test_status_error_on_non_pdf(self, non_pdf_path):
        result = process_medical_pdf(non_pdf_path)
        assert result["status"] == "error"

    def test_empty_pdf_succeeds_with_warnings(self, empty_pdf_path):
        result = process_medical_pdf(empty_pdf_path)
        assert result["status"] == "success"
        assert len(result["warnings"]) > 0

    def test_multipage_pdf_correct_page_count(self, multipage_pdf_path):
        result = process_medical_pdf(multipage_pdf_path)
        assert result["total_pages"] == 3


class TestGetDocumentChunks:
    def test_returns_list(self, valid_pdf_path):
        doc = process_medical_pdf(valid_pdf_path)
        chunks = get_document_chunks(doc)
        assert isinstance(chunks, list)

    def test_chunks_not_empty_for_valid_doc(self, valid_pdf_path):
        doc = process_medical_pdf(valid_pdf_path)
        chunks = get_document_chunks(doc)
        assert len(chunks) > 0

    def test_chunk_has_required_keys(self, valid_pdf_path):
        doc = process_medical_pdf(valid_pdf_path)
        chunks = get_document_chunks(doc)
        required_keys = {
            "chunk_id", "document_id", "filename",
            "page_number", "chunk_index", "text",
            "char_count", "start_char", "end_char"
        }
        for chunk in chunks:
            assert required_keys.issubset(chunk.keys())

    def test_document_id_consistent(self, valid_pdf_path):
        doc = process_medical_pdf(valid_pdf_path)
        chunks = get_document_chunks(doc)
        for chunk in chunks:
            assert chunk["document_id"] == doc["document_id"]

    def test_chunk_ids_unique(self, valid_pdf_path):
        doc = process_medical_pdf(valid_pdf_path)
        chunks = get_document_chunks(doc)
        ids = [c["chunk_id"] for c in chunks]
        assert len(ids) == len(set(ids))

    def test_error_doc_returns_empty_list(self, non_existent_path):
        doc = process_medical_pdf(non_existent_path)
        chunks = get_document_chunks(doc)
        assert chunks == []

    def test_empty_pdf_returns_empty_chunks(self, empty_pdf_path):
        doc = process_medical_pdf(empty_pdf_path)
        chunks = get_document_chunks(doc)
        assert chunks == []

    def test_custom_chunk_size(self, valid_pdf_path):
        doc = process_medical_pdf(valid_pdf_path)
        chunks = get_document_chunks(doc, chunk_size=200, chunk_overlap=20)
        for chunk in chunks:
            assert chunk["char_count"] <= 200

    def test_medical_values_preserved_in_chunks(self, valid_pdf_path):
        doc = process_medical_pdf(valid_pdf_path)
        chunks = get_document_chunks(doc)
        all_text = " ".join(c["text"] for c in chunks)
        assert "13.8" in all_text
        assert "g/dL" in all_text
