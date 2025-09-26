"""
COMP-5700 Exercise 4: IEEE Secure Design Principles (Program Code)
Author: Jacob Murrah
Date: 09/26/2025
"""

from collections import defaultdict
from pathlib import Path

import re
import yaml

from principles import PRINCIPLES

TERMS = {
    "encrypt",
    "encryption",
    "decrypt",
    "cipher",
    "ciphertext",
    "plaintext",
    "hash",
    "hashing",
    "digest",
    "md5",
    "sha",
    "sha256",
    "sha512",
    "bcrypt",
    "scrypt",
    "argon2",
    "rsa",
    "aes",
    "ecb",
    "cbc",
    "gcm",
    "mac",
    "hmac",
    "signature",
    "signing",
    "certificate",
    "tls",
    "random",
    "range",
    "seed",
    "nonce",
    "iv",
    "entropy",
    "algorithm",
    "implementation",
    "custom",
    "own",
    "proprietary",
    "variant",
    "rotate",
    "rotation",
    "key",
    "keys",
    "token",
    "secret",
    "credential",
    "kdf",
    "keystore",
    "vault",
    "policy",
}


# -------------------------
# (T1) include a method/function to parse the YAML content
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
# (T2) include at least one method/function that performs content extraction related to policy violations
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
# (T3) include at least one method/function that performs a key-value based lookup operation to determine violations of the principles
# ------------------------------------------------------------------
def lookup_principle_violations(
    requirement_text: str,
    principles: dict[str, list[dict[str, list[str]]]] = PRINCIPLES,
) -> dict[str, list[str]]:
    """Use keyword lookups to find violations described in principles."""

    text_lower = requirement_text.lower()
    matches = defaultdict(set)

    for principle, violation_entries in principles.items():
        for entry in violation_entries:
            violation = entry["violation"].strip()
            keywords = entry["keywords"]
            if any(keyword.lower() in text_lower for keyword in keywords):
                matches[principle].add(violation)

    return {principle: sorted(violations) for principle, violations in matches.items()}


def analyze_requirements(
    requirements: dict[str, str]
) -> dict[str, dict[str, dict[str]]]:
    """Combine clause extraction and principle lookup for each requirement."""
    analysis = {}
    for req_id, text in requirements.items():
        clauses = extract_security_clauses(
            text, list(TERMS)
        )  # (T2) include at least one method/function that performs content extraction related to policy violations

        violations = lookup_principle_violations(
            text, PRINCIPLES
        )  # (T3) include at least one method/function that performs a key-value based lookup operation to determine violations of the principles

        analysis[req_id] = {
            "clauses": clauses,
            "violations": violations,
        }

    return analysis


def print_report(
    requirements: dict[str, str], analysis: dict[str, dict[str, list[str]]]
) -> None:
    """Render a three-section report with parsed data and detected findings."""

    print("=" * 30)
    print("REQUIREMENTS ANALYSIS REPORT")
    print("=" * 30)

    # Parsed Requirements
    print("📋 PARSED REQUIREMENTS")
    print("-" * 30)
    for req_id, text in requirements.items():
        print(f"• {req_id}: {text}")

    # Detected Violations
    print(f"\n⚠️  DETECTED VIOLATIONS")
    print("-" * 30)
    for req_id, text in requirements.items():
        violations = analysis[req_id]["violations"]
        print(f"📌 {req_id}: {text}")

        if not violations:
            print("   ✅ No violations detected\n")
            continue

        for principle, details in violations.items():
            print(f"   🚨 {principle.title()}:")
            for detail in details:
                print(f"      → {detail}\n")

    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 30)
    requirements_count = len(requirements)
    requirements_with_violations = sum(
        1 for info in analysis.values() if info["violations"]
    )
    total_violations = sum(len(info["violations"]) for info in analysis.values())

    print(f"Total requirements processed: {requirements_count}")
    print(f"Requirements with violations: {requirements_with_violations}")
    print(f"Total violation categories: {total_violations}")

    if requirements_with_violations == 0:
        print("\n🎉 All requirements passed validation!")
    else:
        compliance_rate = (
            (requirements_count - requirements_with_violations) / requirements_count
        ) * 100
        print(f"Compliance rate: {compliance_rate:.1f}%")

    print("-" * 30)


if __name__ == "__main__":
    requirements = parse_requirements_yaml(
        "requirements.yaml"
    )  # (T1) include a method/function to parse the YAML content
    analysis_result = analyze_requirements(requirements)
    print_report(requirements, analysis_result)
