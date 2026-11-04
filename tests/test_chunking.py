"""
test_chunking.py
Tests for semantic chunking and metadata completeness.
"""

import pytest
from document_processing.chunking import chunk_text, chunk_document


SAMPLE_TEXT = (
    "Hemoglobin: 13.8 g/dL  Reference: 13.5 - 17.5 g/dL\n"
    "Hematocrit: 41.2 %  Reference: 41 - 53 %\n"
    "RBC Count: 4.70 x10^6/uL  Reference: 4.5 - 5.9 x10^6/uL\n"
    "WBC Count: 7200 cells/uL  Reference: 4500 - 11000 cells/uL\n"
    "Platelet Count: 220000 /uL  Reference: 150000 - 400000 /uL\n"
    "Fasting Glucose: 92 mg/dL  Reference: 70 - 99 mg/dL\n"
    "Total Cholesterol: 185 mg/dL  Reference: < 200 mg/dL\n"
    "Creatinine: 0.95 mg/dL  Reference: 0.74 - 1.35 mg/dL\n"
    "TSH: 2.10 mIU/L  Reference: 0.4 - 4.0 mIU/L\n"
)


class TestChunkText:
    def test_returns_list(self):
        chunks = chunk_text(SAMPLE_TEXT, "doc1", "test.pdf", page_number=1)
        assert isinstance(chunks, list)

    def test_chunks_not_empty_for_valid_text(self):
        chunks = chunk_text(SAMPLE_TEXT, "doc1", "test.pdf")
        assert len(chunks) > 0

    def test_empty_text_returns_empty_list(self):
        chunks = chunk_text("", "doc1", "test.pdf")
        assert chunks == []

    def test_whitespace_only_returns_empty_list(self):
        chunks = chunk_text("   \n\n  ", "doc1", "test.pdf")
        assert chunks == []

    def test_chunk_metadata_keys(self):
        chunks = chunk_text(SAMPLE_TEXT, "doc1", "test.pdf", page_number=2)
        for chunk in chunks:
            assert "chunk_id" in chunk
            assert "document_id" in chunk
            assert "filename" in chunk
            assert "page_number" in chunk
            assert "chunk_index" in chunk
            assert "text" in chunk
            assert "char_count" in chunk
            assert "start_char" in chunk
            assert "end_char" in chunk

    def test_document_id_in_chunks(self):
        chunks = chunk_text(SAMPLE_TEXT, "my-doc-id", "report.pdf")
        for chunk in chunks:
            assert chunk["document_id"] == "my-doc-id"

    def test_filename_in_chunks(self):
        chunks = chunk_text(SAMPLE_TEXT, "doc1", "report.pdf")
        for chunk in chunks:
            assert chunk["filename"] == "report.pdf"

    def test_page_number_in_chunks(self):
        chunks = chunk_text(SAMPLE_TEXT, "doc1", "report.pdf", page_number=3)
        for chunk in chunks:
            assert chunk["page_number"] == 3

    def test_chunk_index_sequential(self):
        chunks = chunk_text(SAMPLE_TEXT, "doc1", "report.pdf", chunk_size=100, chunk_overlap=20)
        indices = [c["chunk_index"] for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_chunk_ids_are_unique(self):
        chunks = chunk_text(SAMPLE_TEXT, "doc1", "report.pdf", chunk_size=100, chunk_overlap=20)
        ids = [c["chunk_id"] for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_size_respected(self):
        size = 150
        chunks = chunk_text(SAMPLE_TEXT, "doc1", "report.pdf", chunk_size=size, chunk_overlap=0)
        for chunk in chunks:
            assert chunk["char_count"] <= size

    def test_overlap_creates_more_chunks_than_no_overlap(self):
        no_overlap = chunk_text(SAMPLE_TEXT, "doc1", "f.pdf", chunk_size=100, chunk_overlap=0)
        with_overlap = chunk_text(SAMPLE_TEXT, "doc1", "f.pdf", chunk_size=100, chunk_overlap=30)
        assert len(with_overlap) >= len(no_overlap)

    def test_invalid_chunk_size_raises(self):
        with pytest.raises(ValueError):
            chunk_text(SAMPLE_TEXT, "doc1", "f.pdf", chunk_size=0)

    def test_overlap_gte_size_raises(self):
        with pytest.raises(ValueError):
            chunk_text(SAMPLE_TEXT, "doc1", "f.pdf", chunk_size=100, chunk_overlap=100)

    def test_medical_values_preserved_in_chunks(self):
        chunks = chunk_text(SAMPLE_TEXT, "doc1", "report.pdf", chunk_size=500, chunk_overlap=0)
        all_text = " ".join(c["text"] for c in chunks)
        assert "13.8" in all_text
        assert "g/dL" in all_text
        assert "92" in all_text
        assert "mg/dL" in all_text


class TestChunkDocument:
    def _make_extraction(self, text: str, doc_id="doc-1", filename="report.pdf"):
        return {
            "document_id": doc_id,
            "filename": filename,
            "pages": [
                {
                    "page_number": 1,
                    "text": text,
                    "is_empty": not text.strip(),
                }
            ],
        }

    def test_chunk_document_returns_list(self):
        extraction = self._make_extraction(SAMPLE_TEXT)
        chunks = chunk_document(extraction)
        assert isinstance(chunks, list)

    def test_chunk_document_empty_page_skipped(self):
        extraction = self._make_extraction("")
        chunks = chunk_document(extraction)
        assert chunks == []

    def test_chunk_document_multi_page(self):
        extraction = {
            "document_id": "doc-2",
            "filename": "multi.pdf",
            "pages": [
                {"page_number": 1, "text": SAMPLE_TEXT, "is_empty": False},
                {"page_number": 2, "text": "Second page content with TSH: 2.1 mIU/L", "is_empty": False},
            ],
        }
        chunks = chunk_document(extraction)
        page_nums = {c["page_number"] for c in chunks}
        assert 1 in page_nums
        assert 2 in page_nums
