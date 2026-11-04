"""
test_pdf_extractor.py
Tests for PDF validation and text extraction.
"""

import pytest
from document_processing.pdf_extractor import validate_pdf, extract_text_from_pdf, PDFExtractionError


# ---------------------------------------------------------------------------
# validate_pdf
# ---------------------------------------------------------------------------

class TestValidatePdf:
    def test_valid_pdf_returns_true(self, valid_pdf_path):
        result = validate_pdf(valid_pdf_path)
        assert result["valid"] is True
        assert result["reason"] == "OK"

    def test_non_existent_file(self, non_existent_path):
        result = validate_pdf(non_existent_path)
        assert result["valid"] is False
        assert "not found" in result["reason"].lower()

    def test_wrong_extension(self, non_pdf_path):
        result = validate_pdf(non_pdf_path)
        assert result["valid"] is False
        assert "invalid file type" in result["reason"].lower()

    def test_corrupted_pdf(self, corrupted_pdf_path):
        result = validate_pdf(corrupted_pdf_path)
        assert result["valid"] is False

    def test_empty_file(self, tmp_path):
        empty = tmp_path / "empty.pdf"
        empty.write_bytes(b"")
        result = validate_pdf(str(empty))
        assert result["valid"] is False
        assert "empty" in result["reason"].lower()


# ---------------------------------------------------------------------------
# extract_text_from_pdf
# ---------------------------------------------------------------------------

class TestExtractTextFromPdf:
    def test_extraction_returns_expected_keys(self, valid_pdf_path):
        result = extract_text_from_pdf(valid_pdf_path)
        for key in ("file_path", "filename", "total_pages", "pages", "full_text", "warnings"):
            assert key in result

    def test_page_count(self, valid_pdf_path):
        result = extract_text_from_pdf(valid_pdf_path)
        assert result["total_pages"] == 2

    def test_multipage_count(self, multipage_pdf_path):
        result = extract_text_from_pdf(multipage_pdf_path)
        assert result["total_pages"] == 3

    def test_full_text_not_empty(self, valid_pdf_path):
        result = extract_text_from_pdf(valid_pdf_path)
        assert result["full_text"].strip() != ""

    def test_page_metadata_fields(self, valid_pdf_path):
        result = extract_text_from_pdf(valid_pdf_path)
        for page in result["pages"]:
            assert "page_number" in page
            assert "text" in page
            assert "char_count" in page
            assert "is_empty" in page
            assert "extraction_note" in page

    def test_page_numbers_are_one_based(self, valid_pdf_path):
        result = extract_text_from_pdf(valid_pdf_path)
        page_nums = [p["page_number"] for p in result["pages"]]
        assert page_nums[0] == 1

    def test_empty_pdf_produces_warning(self, empty_pdf_path):
        result = extract_text_from_pdf(empty_pdf_path)
        assert len(result["warnings"]) > 0

    def test_empty_pdf_full_text_is_blank(self, empty_pdf_path):
        result = extract_text_from_pdf(empty_pdf_path)
        assert result["full_text"].strip() == ""

    def test_invalid_pdf_raises_error(self, non_existent_path):
        with pytest.raises(PDFExtractionError):
            extract_text_from_pdf(non_existent_path)

    def test_corrupted_pdf_raises_error(self, corrupted_pdf_path):
        with pytest.raises(PDFExtractionError):
            extract_text_from_pdf(corrupted_pdf_path)
