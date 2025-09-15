"""
COMP-5700 Exercise 4: IEEE Secure Design Principles
Author: Jacob Murrah
Date: 09/03/2025
"""

import yaml
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from cryptographic_principles import PRINCIPLES


def parse_yaml(file_path="requirements.yaml"):
    with open(file_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        return data


def extract_key_value_requirements(yaml_content):
    if not yaml_content or not isinstance(yaml_content, list):
        return {}

    yaml_string = yaml_content[0]

    pattern = r'(\w+):"([^"]*)"'
    matches = re.findall(pattern, yaml_string)

    # extract only the requirements
    key_value_dict = {key: value for key, value in matches if key != "ALL"}
    return key_value_dict


# ---------- Models ----------
def build_models():
    # Zero-shot: BART-MNLI (broad recall). Uses label->hypothesis internally.
    # We provide fully formed hypotheses, so hypothesis_template="{}" is fine.
    tok = AutoTokenizer.from_pretrained("cross-encoder/nli-deberta-v3-base")
    nli = AutoModelForSequenceClassification.from_pretrained("cross-encoder/nli-deberta-v3-base")
    return tok, nli


# ---------- Inference ----------
def entailment(premise: str, hypothesis: str, tok, nli) -> float:
    """Return P(entailment) for (premise, hypothesis)."""
    inputs = tok(premise, hypothesis, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = nli(**inputs).logits[
            0
        ]  # [contradiction, entailment, neutral] per model card
    probs = torch.softmax(logits, dim=-1).tolist()
    return float(probs[1])


def analyze_requirement(req_text: str, principles: dict, tok, nli) -> dict:
    out = {"text": req_text, "violations": [], "compliance": []}

    # 1) Score all violation hypotheses directly (no zero-shot shortlist)
    TH_DEFAULT = 0.60
    TH_NO_CUSTOM = 0.70

    per_pid = {}          # pid -> max entailment
    per_pid_matches = {}  # pid -> list of matched claims

    for pid, p in principles.items():
        for claim in p.get("violations", []):
            e = entailment(req_text, claim, tok, nli)
            if e >= (TH_NO_CUSTOM if pid == "NO_CUSTOM_CRYPTO" else TH_DEFAULT):
                per_pid[pid] = max(per_pid.get(pid, 0.0), e)
                per_pid_matches.setdefault(pid, []).append(
                    {"principle": pid, "claim": claim, "entailment": round(e, 3)}
                )

    # 2) Compliance cues (positive signals)
    for pid, p in principles.items():
        for cclaim in p.get("compliance", []):
            e = entailment(req_text, cclaim, tok, nli)
            if e >= TH_DEFAULT:
                out["compliance"].append(
                    {"principle": pid, "claim": cclaim, "entailment": round(e, 3)}
                )

    # 3) Optional guardrail: if it clearly uses vetted libs, downweight NO_CUSTOM_CRYPTO
    guard = "This requirement mandates using vetted, industry-standard crypto libraries."
    if "NO_CUSTOM_CRYPTO" in per_pid:
        e_guard = entailment(req_text, guard, tok, nli)
        if e_guard >= 0.60:
            per_pid.pop("NO_CUSTOM_CRYPTO", None)
            per_pid_matches.pop("NO_CUSTOM_CRYPTO", None)

    # 4) Finalize
    for pid, score in sorted(per_pid.items(), key=lambda x: x[1], reverse=True):
        out["violations"].append({
            "principle": pid,
            "score": round(score, 3),
            "matches": per_pid_matches[pid]
        })
    return out


def print_analysis_summary(requirements_analysis):
    """Print a clean summary of the analysis."""
    print("\n" + "="*80)
    print("CRYPTOGRAPHIC SECURITY PRINCIPLES VIOLATION ANALYSIS")
    print("="*80)
    
    for req_id, analysis in requirements_analysis.items():
        print(f"\n{req_id}: {analysis['text']}")
        print("-" * 60)
        
        if analysis['violations']:
            print(f"VIOLATIONS ({len(analysis['violations'])}):")
            for violation in analysis['violations']:
                print(f"  ❌ {violation['principle']} (Score: {violation['score']})")
                for match in violation['matches']:
                    print(f"     - {match['claim']} ({match['entailment']})")
        
        if analysis['compliance']:
            print(f"COMPLIANCE ({len(analysis['compliance'])}):")
            for compliance in analysis['compliance']:
                print(f"  ✅ {compliance['principle']} (Score: {compliance['entailment']})")
                print(f"     - {compliance['claim']}")
        
        if not analysis['violations'] and not analysis['compliance']:
            print("  No significant violations or compliance indicators detected")
        
        print("-" * 60)


# ---------- CLI ----------
if __name__ == "__main__":
    print("Loading models and analyzing requirements...")
    
    # Parse requirements
    yaml_content = parse_yaml()
    requirements = extract_key_value_requirements(yaml_content)
    
    # Build models
    tok, nli = build_models()
    
    # Analyze each requirement once
    requirements_analysis = {}
    for rid, txt in requirements.items():
        print(f"Analyzing {rid}...")
        analysis = analyze_requirement(txt, PRINCIPLES, tok, nli)
        requirements_analysis[rid] = analysis
    
    # Print clean summary
    print_analysis_summary(requirements_analysis)
    
    # Print brief results for debugging
    print("\nBrief Results:")
    for rid, analysis in requirements_analysis.items():
        violations = [v['principle'] for v in analysis['violations']]
        compliance = [c['principle'] for c in analysis['compliance']]
        print(f"{rid}: Violations={violations}, Compliance={compliance}")