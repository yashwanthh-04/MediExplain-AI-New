"""
glossary_loader.py
Loads and queries the medical glossary JSON file.
"""

import json
import os
from typing import Optional, List, Dict, Any

# Resolve path relative to this file so it works from any working directory
_GLOSSARY_PATH = os.path.join(os.path.dirname(__file__), "medical_glossary.json")


def load_glossary(path: str = _GLOSSARY_PATH) -> Dict[str, Any]:
    """
    Load the full glossary from a JSON file.

    Args:
        path: Path to the glossary JSON. Defaults to the bundled file.

    Returns:
        Parsed glossary dict with 'metadata' and 'terms' keys.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the JSON is malformed.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Glossary file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Glossary JSON is malformed: {e}")

    if "terms" not in data:
        raise ValueError("Glossary JSON missing required 'terms' key.")

    return data


def get_term(term_key: str, path: str = _GLOSSARY_PATH) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single term entry by its key (case-insensitive).

    Args:
        term_key: e.g. "hemoglobin", "wbc", "tsh"
        path:     Path to glossary JSON (optional override).

    Returns:
        The term dict, or None if not found.
    """
    glossary = load_glossary(path)
    return glossary["terms"].get(term_key.lower())


def list_terms(path: str = _GLOSSARY_PATH) -> List[str]:
    """
    Return all term keys available in the glossary.

    Returns:
        Sorted list of term key strings.
    """
    glossary = load_glossary(path)
    return sorted(glossary["terms"].keys())
