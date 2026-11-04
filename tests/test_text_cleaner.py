"""
test_text_cleaner.py
Tests for medical text cleaning – especially value preservation.
"""

from document_processing.text_cleaner import clean_medical_text


class TestCleanMedicalText:
    def test_empty_string_returns_empty(self):
        assert clean_medical_text("") == ""

    def test_none_equivalent_empty(self):
        assert clean_medical_text("") == ""

    def test_strips_leading_trailing_whitespace(self):
        result = clean_medical_text("   hello   ")
        assert result == "hello"

    def test_collapses_multiple_blank_lines(self):
        text = "line1\n\n\n\nline2"
        result = clean_medical_text(text)
        assert "\n\n\n" not in result

    def test_removes_form_feed(self):
        text = "page1\fpage2"
        result = clean_medical_text(text)
        assert "\f" not in result

    def test_removes_null_bytes(self):
        text = "value\x00test"
        result = clean_medical_text(text)
        assert "\x00" not in result

    # --- Medical value preservation ---

    def test_preserves_decimal_values(self):
        text = "Hemoglobin: 13.8 g/dL"
        result = clean_medical_text(text)
        assert "13.8" in result

    def test_preserves_units_gdl(self):
        text = "Hemoglobin: 13.8 g/dL"
        result = clean_medical_text(text)
        assert "g/dL" in result

    def test_preserves_reference_range_with_dash(self):
        text = "Reference: 13.5 - 17.5 g/dL"
        result = clean_medical_text(text)
        assert "13.5" in result
        assert "17.5" in result

    def test_preserves_date_slash_format(self):
        text = "Date: 11/04/2026"
        result = clean_medical_text(text)
        assert "11/04/2026" in result

    def test_preserves_date_iso_format(self):
        text = "Date: 2026-11-04"
        result = clean_medical_text(text)
        assert "2026-11-04" in result

    def test_preserves_mg_dl_unit(self):
        text = "Glucose: 92 mg/dL"
        result = clean_medical_text(text)
        assert "mg/dL" in result
        assert "92" in result

    def test_preserves_scientific_notation_unit(self):
        text = "RBC: 4.70 x10^6/uL"
        result = clean_medical_text(text)
        assert "4.70" in result
        assert "x10^6/uL" in result

    def test_preserves_miu_l_unit(self):
        text = "TSH: 2.10 mIU/L"
        result = clean_medical_text(text)
        assert "2.10" in result
        assert "mIU/L" in result

    def test_collapses_extra_spaces_on_line(self):
        text = "Hemoglobin:    13.8   g/dL"
        result = clean_medical_text(text)
        # Multiple spaces collapsed but values intact
        assert "13.8" in result
        assert "g/dL" in result
        assert "  " not in result  # no double spaces remain

    def test_preserves_test_names(self):
        text = "Platelet Count: 220000 /uL"
        result = clean_medical_text(text)
        assert "Platelet Count" in result

    def test_multiline_report_preserved(self):
        text = (
            "Hemoglobin: 13.8 g/dL\n"
            "Hematocrit: 41.2 %\n"
            "RBC Count:  4.70 x10^6/uL\n"
        )
        result = clean_medical_text(text)
        assert "13.8" in result
        assert "41.2" in result
        assert "4.70" in result
