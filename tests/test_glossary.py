"""
test_glossary.py
Tests for the medical knowledge base / glossary loader.
"""

import json
import pytest
from medical_knowledge.glossary_loader import load_glossary, get_term, list_terms


class TestLoadGlossary:
    def test_loads_successfully(self):
        glossary = load_glossary()
        assert isinstance(glossary, dict)

    def test_has_metadata_key(self):
        glossary = load_glossary()
        assert "metadata" in glossary

    def test_has_terms_key(self):
        glossary = load_glossary()
        assert "terms" in glossary

    def test_terms_is_dict(self):
        glossary = load_glossary()
        assert isinstance(glossary["terms"], dict)

    def test_all_required_terms_present(self):
        required = {
            "hemoglobin", "rbc", "wbc", "platelets", "glucose",
            "cholesterol", "creatinine", "vitamin_d", "tsh", "hematocrit"
        }
        glossary = load_glossary()
        assert required.issubset(set(glossary["terms"].keys()))

    def test_file_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_glossary(str(tmp_path / "missing.json"))

    def test_malformed_json_raises(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{ not valid json !!!")
        with pytest.raises(ValueError, match="malformed"):
            load_glossary(str(bad))

    def test_missing_terms_key_raises(self, tmp_path):
        bad = tmp_path / "notterms.json"
        bad.write_text(json.dumps({"metadata": {}}))
        with pytest.raises(ValueError, match="terms"):
            load_glossary(str(bad))


class TestGetTerm:
    @pytest.mark.parametrize("term_key", [
        "hemoglobin", "rbc", "wbc", "platelets", "glucose",
        "cholesterol", "creatinine", "vitamin_d", "tsh", "hematocrit"
    ])
    def test_known_term_returns_dict(self, term_key):
        result = get_term(term_key)
        assert result is not None
        assert isinstance(result, dict)

    def test_unknown_term_returns_none(self):
        assert get_term("nonexistent_term_xyz") is None

    def test_case_insensitive_lookup(self):
        assert get_term("HEMOGLOBIN") is not None
        assert get_term("Hemoglobin") is not None

    def test_term_has_definition(self):
        term = get_term("hemoglobin")
        assert "definition" in term
        assert len(term["definition"]) > 10

    def test_term_has_reference_range(self):
        term = get_term("hemoglobin")
        assert "typical_reference_range" in term

    def test_term_has_source(self):
        term = get_term("hemoglobin")
        assert "source" in term

    def test_term_has_source_url(self):
        term = get_term("hemoglobin")
        assert "source_url" in term
        assert term["source_url"].startswith("https://")

    def test_term_has_clinical_significance(self):
        term = get_term("glucose")
        assert "clinical_significance" in term


class TestListTerms:
    def test_returns_list(self):
        terms = list_terms()
        assert isinstance(terms, list)

    def test_list_is_sorted(self):
        terms = list_terms()
        assert terms == sorted(terms)

    def test_list_has_ten_terms(self):
        terms = list_terms()
        assert len(terms) == 10

    def test_list_contains_known_term(self):
        terms = list_terms()
        assert "hemoglobin" in terms
