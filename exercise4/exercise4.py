from collections import defaultdict
from pathlib import Path

import re

import torch

import yaml
from transformers import pipeline


from principles import PRINCIPLES

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

NLP_SCORE_THRESHOLD = 0.45
ZERO_SHOT_CLASSIFIER = pipeline(
    "zero-shot-classification",
    model="jackaduma/SecBERT",
    tokenizer="jackaduma/SecBERT",
    device=0 if torch.cuda.is_available() else -1,
)


# -------------------------
# (T1) YAML parsing helpers
# -------------------------
def parse_requirements_yaml(path: str) -> dict[str, str]:
    """Parse the exercise requirements YAML into a mapping of IDs to statements."""

    def parse_requirements_from_string(raw: str) -> dict[str, str]:
        """Parser for the compact YAML format with inline key-value pairs."""
        pattern = re.compile(r"(\w+):\"([^\"]*)\"")
        matches = pattern.findall(raw)
        requirements = {}
        for key, value in matches:
            if key == "ALL":
                continue
            requirements[key] = value.strip()
        return requirements

    file_path = Path(path)
    try:
        raw_data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Requirements file not found: {file_path}") from exc

    if not isinstance(raw_data, list) or not raw_data:
        raise ValueError("YAML content must be a non-empty list of mappings.")

    entry = raw_data[0]
    if isinstance(entry, str):
        requirements = parse_requirements_from_string(entry)
    elif isinstance(entry, dict):
        requirements = {}
        for key, value in entry.items():
            if key == "ALL":
                continue
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("Requirement identifiers and text must be strings.")
            requirements[key] = value.strip()
    else:
        raise ValueError("The YAML root list must contain str or mapping objects.")

    if not requirements:
        raise ValueError("No requirement entries were found in the YAML file.")

    return requirements


# ------------------------------------------------------
# (T2) Content extraction for potential policy violations
# ------------------------------------------------------
def extract_security_clauses(requirement_text: str, terms: list[str]) -> list[str]:
    """Return clauses that contain terms suggesting cryptography policy decisions."""

    def split_into_clauses(text: str) -> list[str]:
        """Split a text into clauses based on punctuation."""
        parts = [
            segment.strip()
            for segment in re.compile(r"(?<=[.!?])\s+|;\s+").split(text)
            if segment.strip()
        ]
        return parts or [text.strip()]

    if not requirement_text:
        return []

    terms = set(t.lower() for t in terms)

    clauses = []
    for clause in split_into_clauses(requirement_text):
        clause_lower = clause.lower()
        if any(term in clause_lower for term in terms):
            clauses.append(clause)

    if not clauses:
        clauses.append(requirement_text.strip())

    return clauses


# ------------------------------------------------------------------
# (T3) Key-value based lookup against the secure design principles map
# ------------------------------------------------------------------
def lookup_principle_violations(
    requirement_text: str,
    principles: dict[str, list[dict[str, list[str]]]] = PRINCIPLES,
) -> dict[str, list[str]]:
    """Use keyword lookups to find violations described in principles."""

    text_lower = requirement_text.lower()
    matches = defaultdict(set)

    for principle, violation_entries in principles.items():
        candidate_labels = []
        for entry in violation_entries:
            violation = entry["violation"].strip()
            keywords = entry["keywords"]
            candidate_labels.append(violation)
            if any(keyword.lower() in text_lower for keyword in keywords):
                matches[principle].add(violation)

        if candidate_labels:
            result = ZERO_SHOT_CLASSIFIER(
                requirement_text,
                candidate_labels=candidate_labels,
                multi_label=True,
            )
            for label, score in zip(result["labels"], result["scores"]):
                if score >= NLP_SCORE_THRESHOLD:
                    matches[principle].add(label)

    return {principle: sorted(violations) for principle, violations in matches.items()}


# ------------------------
# Analysis and formatting
# ------------------------
def analyze_requirements(
    requirements: dict[str, str]
) -> dict[str, dict[str, dict[str]]]:
    """Combine clause extraction and principle lookup for each requirement."""
    analysis = {}
    for req_id, text in requirements.items():
        clauses = extract_security_clauses(text, list(INTERESTING_TERMS))
        violations = lookup_principle_violations(text, PRINCIPLES)
        analysis[req_id] = {
            "clauses": clauses,
            "violations": violations,
        }

    return analysis


def print_report(
    requirements: dict[str, str], analysis: dict[str, dict[str, list[str]]]
) -> None:
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
    print(
        f"  Requirements with violations: {sum(bool(info['violations']) for info in analysis.values())}"
    )
    print(f"  Principle categories flagged: {total_violations}")


if __name__ == "__main__":
    requirements = parse_requirements_yaml("requirements.yaml")
    analysis_result = analyze_requirements(requirements)
    print_report(requirements, analysis_result)
