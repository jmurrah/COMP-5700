"""Utility for flagging cryptography design violations from YAML requirements."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping

import re
import yaml

try:  # pragma: no cover - exercised when running as a script
    from .principles import PRINCIPLES
except ImportError:  # pragma: no cover - exercised when module is executed directly
    from principles import PRINCIPLES

# Keywords that hint at potentially risky cryptography statements.
INTERESTING_TERMS = {
    "encrypt",
    "hash",
    "md5",
    "sha",
    "random",
    "range",
    "seed",
    "nonce",
    "algorithm",
    "implementation",
    "custom",
    "own",
    "rotate",
    "key",
}

DEFAULT_REQUIREMENTS_PATH = Path(__file__).with_name("requirements.yaml")


# -------------------------
# (T1) YAML parsing helpers
# -------------------------
def parse_requirements_yaml(path: str | Path = DEFAULT_REQUIREMENTS_PATH) -> Dict[str, str]:
    """Parse the exercise requirements YAML into a mapping of IDs to statements."""

    file_path = Path(path)
    try:
        raw_data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:  # pragma: no cover - defensive guard
        raise FileNotFoundError(f"Requirements file not found: {file_path}") from exc

    if not isinstance(raw_data, list) or not raw_data:
        raise ValueError("YAML content must be a non-empty list of mappings.")

    entry = raw_data[0]
    if isinstance(entry, str):
        requirements = _parse_requirements_from_string(entry)
    elif isinstance(entry, Mapping):
        requirements = {}
        for key, value in entry.items():
            if key == "ALL":
                continue
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("Requirement identifiers and text must be strings.")
            requirements[key] = value.strip()
    else:
        raise ValueError("The YAML root list must contain mapping objects.")

    if not requirements:
        raise ValueError("No requirement entries were found in the YAML file.")

    return requirements


# ------------------------------------------------------
# (T2) Content extraction for potential policy violations
# ------------------------------------------------------
def extract_security_clauses(requirement_text: str, terms: Iterable[str] | None = None) -> List[str]:
    """Return clauses that contain terms suggesting cryptography policy decisions."""

    if not requirement_text:
        return []

    terms = set(t.lower() for t in (terms or INTERESTING_TERMS))
    clauses = []

    for clause in _split_into_clauses(requirement_text):
        clause_lower = clause.lower()
        if any(term in clause_lower for term in terms):
            clauses.append(clause)

    # Ensure we keep at least the original requirement for downstream context.
    if not clauses:
        clauses.append(requirement_text.strip())

    return clauses


_SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+|;\s+")


def _split_into_clauses(text: str) -> List[str]:
    parts = [segment.strip() for segment in _SENTENCE_SPLIT_REGEX.split(text) if segment.strip()]
    return parts or [text.strip()]


def _parse_requirements_from_string(raw: str) -> Dict[str, str]:
    """Fallback parser for the compact YAML format used by the starter file."""

    pattern = re.compile(r"(\w+):\"([^\"]*)\"")
    matches = pattern.findall(raw)
    requirements: Dict[str, str] = {}
    for key, value in matches:
        if key == "ALL":
            continue
        requirements[key] = value.strip()
    return requirements


# ------------------------------------------------------------------
# (T3) Key-value based lookup against the secure design principles map
# ------------------------------------------------------------------
def lookup_principle_violations(requirement_text: str, principles: Mapping[str, List[Mapping[str, List[str]]]] = PRINCIPLES) -> Dict[str, List[str]]:
    """Use keyword lookups to find violations described in principles."""

    text_lower = requirement_text.lower()
    matches: Dict[str, set[str]] = defaultdict(set)

    for principle, violation_entries in principles.items():
        for entry in violation_entries:
            violation = entry.get("violation", "").strip()
            keywords = entry.get("keywords", [])
            if not violation or not keywords:
                continue
            if any(keyword.lower() in text_lower for keyword in keywords):
                matches[principle].add(violation)

    return {principle: sorted(violations) for principle, violations in matches.items()}


# ------------------------
# Analysis and formatting
# ------------------------
def analyze_requirements(requirements: Mapping[str, str]) -> Dict[str, Dict[str, List[str]]]:
    """Combine clause extraction and principle lookup for each requirement."""

    analysis: Dict[str, Dict[str, List[str]]] = {}

    for req_id, text in requirements.items():
        clauses = extract_security_clauses(text)
        violations = lookup_principle_violations(text)
        analysis[req_id] = {
            "clauses": clauses,
            "violations": violations,
        }

    return analysis


def print_report(requirements: Mapping[str, str], analysis: Mapping[str, Dict[str, List[str]]]) -> None:
    """Render a three-section report with parsed data and detected findings."""

    print("Section 1: Parsed Requirements")
    for req_id, text in requirements.items():
        print(f"  {req_id}: {text}")

    print("\nSection 2: Detected Violations")
    for req_id, text in requirements.items():
        req_analysis = analysis[req_id]
        clauses = req_analysis["clauses"]
        clause_list = "; ".join(clauses)
        print(f"  {req_id}: {text}")
        print(f"    Focus clauses: {clause_list}")
        violations = req_analysis["violations"]
        if not violations:
            print("    No violations detected.")
            continue
        for principle, details in violations.items():
            print(f"    {principle}:")
            for detail in details:
                print(f"      - {detail}")

    total_violations = sum(len(info["violations"]) for info in analysis.values())
    print("\nSection 3: Summary")
    print(f"  Requirements processed: {len(requirements)}")
    print(f"  Requirements with violations: {sum(bool(info['violations']) for info in analysis.values())}")
    print(f"  Principle categories flagged: {total_violations}")


if __name__ == "__main__":
    requirements_map = parse_requirements_yaml()
    analysis_result = analyze_requirements(requirements_map)
    print_report(requirements_map, analysis_result)
