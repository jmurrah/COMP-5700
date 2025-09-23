import yaml
import re
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from principles import PRINCIPLES
# --- Core Functions ---
def parse_requirements(yaml_string: str) -> dict:
    """Parses a YAML string and extracts key-value pairs representing requirements."""
    try:
        data = yaml.safe_load(yaml_string)
        requirements = data[0]
        return {key: value for key, value in requirements.items() if re.match(r'^R\d+$', key)}
    except (yaml.YAMLError, IndexError):
        print("⚠️ Warning: Could not parse YAML content.")
        return {}

def get_embedding(text, model, tokenizer, device):
    """Calculates a sentence embedding for the given text using the provided model."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to(device)
    with torch.no_grad():
        model_output = model(**inputs)
    token_embeddings = model_output.last_hidden_state
    attention_mask = inputs['attention_mask']
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return (sum_embeddings / sum_mask)[0]

def analyze_requirements_hybrid(requirements_dict: dict, principles: dict, similarity_threshold=0.60) -> dict:
    """Analyzes requirements using a hybrid keyword-first, then SecBERT semantic-confirmation approach."""
    print("Loading SecBERT model... (This may take a moment on first run)")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained("jackaduma/SecBERT")
    model = AutoModel.from_pretrained("jackaduma/SecBERT").to(device)
    
    all_rules = [{"principle": principle, **rule} for principle, rules_list in principles.items() for rule in rules_list]
    violation_embeddings = {rule['violation']: get_embedding(rule['violation'], model, tokenizer, device) for rule in all_rules}
    analysis_results = {}
    
    for req_id, text in requirements_dict.items():
        print(f"🔬 Analyzing [{req_id}]: '{text}'")
        
        positive_indicators = ["rotated", "if a new", "will be upgraded"]
        if any(indicator in text.lower() for indicator in positive_indicators):
            analysis_results[req_id] = {"text": text, "violations": {}}
            continue

        requirement_embedding = get_embedding(text, model, tokenizer, device)
        confirmed_violations = {}
        
        keyword_matches = [rule for rule in all_rules if any(re.search(r'\b' + re.escape(kw) + r'\b', text.lower()) for kw in rule['keywords'])]
        target_rules = keyword_matches if keyword_matches else all_rules
        
        for rule in target_rules:
            violation_desc = rule['violation']
            principle_name = rule['principle']
            
            # THE FIX IS HERE: Added dim=0
            score = F.cosine_similarity(requirement_embedding, violation_embeddings[violation_desc], dim=0).item()
            
            is_keyword_match = rule in keyword_matches
            current_threshold = 0.50 if is_keyword_match else similarity_threshold

            if score >= current_threshold:
                if principle_name not in confirmed_violations:
                    confirmed_violations[principle_name] = []
                
                confirmed_violations[principle_name].append({
                    "description": violation_desc, 
                    "similarity": f"{score:.2%}",
                    "match_type": "Keyword" if is_keyword_match else "Semantic"
                })
                        
        analysis_results[req_id] = {"text": text, "violations": confirmed_violations}
        
    return analysis_results

# --- Main Execution ---
def main():
    yaml_user_story = """
- ALL: "This user story focuses on specifying clearly specifying crypo-related requirements"
  R1: "We will use MD5 for encrypting all passwords and GitHub API keys."
  R2: "For generating random numbers we will use a fixed range between 39 and 51."
  R3: "We will be using our own implementation of SHA512 to protect API keys."
  R4: "Keys for vault will be rotated."
  R5: "If a new cryptography algorithm comes with better strength, then we will use it instead of SHA512."
"""
    
    requirements = parse_requirements(yaml_user_story)
    
    if requirements:
        analysis = analyze_requirements_hybrid(requirements, PRINCIPLES, similarity_threshold=0.65)
        
        print("\n" + "="*60)
        print(" 🎯 CRYPTOGRAPHIC SECURITY ANALYSIS REPORT (Hybrid Model)")
        print("="*60)
        
        for req_id, result in analysis.items():
            print(f"\n✅ Requirement [{req_id}]: {result['text']}")
            if not result['violations']:
                print("   -> No violations detected.")
            else:
                for principle, violations in result['violations'].items():
                    print(f"   🚨 VIOLATION FOUND: [{principle}]")
                    violations.sort(key=lambda x: (x['match_type'], x['similarity']), reverse=True)
                    for v_info in violations:
                        print(f"      - {v_info['description']} (Similarity: {v_info['similarity']}, Type: {v_info['match_type']})")

if __name__ == "__main__":
    main()