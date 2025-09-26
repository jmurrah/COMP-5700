"""Unit tests for exercise4 cryptography violation detection utilities."""
from __future__ import annotations

from pathlib import Path

import pytest

from exercise4 import (
    analyze_requirements,
    extract_security_clauses,
    lookup_principle_violations,
    parse_requirements_yaml,
)


# -----------------------------
# (i) Tests for YAML parsing
# -----------------------------
def test_parse_requirements_yaml_reads_entries(tmp_path: Path) -> None:
    sample = (
        "- ALL: \"context\"\n"
        "  R1: \"Use MD5 for passwords.\"\n"
        "  R2: \"Rotate keys quarterly.\"\n"
    )
    req_file = tmp_path / "requirements.yaml"
    req_file.write_text(sample, encoding="utf-8")

    result = parse_requirements_yaml(req_file)

    assert result == {
        "R1": "Use MD5 for passwords.",
        "R2": "Rotate keys quarterly.",
    }


def test_parse_requirements_yaml_ignores_all_key(tmp_path: Path) -> None:
    sample = (
        "- ALL: \"overview\"\n"
        "  R1: \"Requirement text\"\n"
    )
    req_file = tmp_path / "req.yaml"
    req_file.write_text(sample, encoding="utf-8")

    result = parse_requirements_yaml(req_file)

    assert "ALL" not in result
    assert list(result.keys()) == ["R1"]


def test_parse_requirements_yaml_supports_compact_format(tmp_path: Path) -> None:
    sample = (
        "- ALL:\"context\"\n"
        "  R1:\"Use MD5 for passwords.\"\n"
        "  R2:\"Rotate keys quarterly.\"\n"
    )
    req_file = tmp_path / "req.yaml"
    req_file.write_text(sample, encoding="utf-8")

    result = parse_requirements_yaml(req_file)

    assert result == {
        "R1": "Use MD5 for passwords.",
        "R2": "Rotate keys quarterly.",
    }


def test_parse_requirements_yaml_rejects_non_list(tmp_path: Path) -> None:
    data = "R1: value\n"
    req_file = tmp_path / "req.yaml"
    req_file.write_text(data, encoding="utf-8")

    with pytest.raises(ValueError):
        parse_requirements_yaml(req_file)


def test_parse_requirements_yaml_rejects_non_mapping(tmp_path: Path) -> None:
    data = "- ['not', 'a', 'mapping']\n"
    req_file = tmp_path / "req.yaml"
    req_file.write_text(data, encoding="utf-8")

    with pytest.raises(ValueError):
        parse_requirements_yaml(req_file)


def test_parse_requirements_yaml_rejects_non_string_values(tmp_path: Path) -> None:
    data = "- R1: 1234\n"
    req_file = tmp_path / "req.yaml"
    req_file.write_text(data, encoding="utf-8")

    with pytest.raises(ValueError):
        parse_requirements_yaml(req_file)


# -----------------------------------------
# (ii) Tests for content extraction helper
# -----------------------------------------
def test_extract_security_clauses_identifies_keyword_clause() -> None:
    text = "We will use MD5 for hashes. Keys rotate annually."
    clauses = extract_security_clauses(text)
    assert "We will use MD5 for hashes." in clauses


def test_extract_security_clauses_handles_multiple_sentences() -> None:
    text = "Random numbers come from a fixed range; custom algorithm ensures speed."
    clauses = extract_security_clauses(text)
    assert len(clauses) == 2


def test_extract_security_clauses_supports_custom_terms() -> None:
    text = "Adopt Argon2 instead of bcrypt."
    clauses = extract_security_clauses(text, terms=["argon2"])
    assert clauses == [text]


def test_extract_security_clauses_returns_full_text_when_no_terms() -> None:
    text = "Performance requirements are pending."
    clauses = extract_security_clauses(text)
    assert clauses == [text]


def test_extract_security_clauses_returns_empty_for_empty_text() -> None:
    assert extract_security_clauses("") == []


# ---------------------------------------------------
# (iii) Tests for principle violation lookups & flow
# ---------------------------------------------------
def test_lookup_principle_violations_detects_md5() -> None:
    text = "Passwords are stored with MD5."
    result = lookup_principle_violations(text)
    assert "PROPER_LIBRARY_USE" in result
    assert any("MD5" in violation for violation in result["PROPER_LIBRARY_USE"])


def test_lookup_principle_violations_detects_custom_algorithm() -> None:
    text = "We rely on our own implementation of AES."
    result = lookup_principle_violations(text)
    assert "NO_CUSTOM_CRYPTO" in result


def test_lookup_principle_violations_is_case_insensitive() -> None:
    text = "Custom SHA variant"
    result = lookup_principle_violations(text)
    assert "NO_CUSTOM_CRYPTO" in result


def test_lookup_principle_violations_deduplicates_entries() -> None:
    principles = {
        "TEST": [
            {"violation": "Uses MD5", "keywords": ["md5", "MD5"]},
            {"violation": "Uses MD5", "keywords": ["md5"]},
        ]
    }
    result = lookup_principle_violations("MD5 is used", principles)
    assert result == {"TEST": ["Uses MD5"]}


def test_lookup_principle_violations_returns_empty_when_clean() -> None:
    text = "Keys are rotated and algorithm updates are reviewed quarterly."
    assert lookup_principle_violations(text) == {}


# ----------------------
# Integration smoke test
# ----------------------
def test_analyze_requirements_combines_helpers(tmp_path: Path) -> None:
    yaml_text = (
        "- ALL: \"context\"\n"
        "  R1: \"Store passwords with MD5.\"\n"
        "  R2: \"Random numbers come from a fixed range.\"\n"
    )
    req_file = tmp_path / "req.yaml"
    req_file.write_text(yaml_text, encoding="utf-8")

    requirements = parse_requirements_yaml(req_file)
    analysis = analyze_requirements(requirements)

    assert set(analysis.keys()) == {"R1", "R2"}
    assert analysis["R1"]["violations"]
    assert analysis["R2"]["violations"]
