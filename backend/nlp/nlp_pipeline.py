import re
from typing import List, Dict, Optional
import os
import json
from pathlib import Path

DISEASE_PATTERNS = {
    "diabetes": [r"\bdiabete[s]?\b", r"\bhigh blood sugar\b", r"\bblood sugar\b", r"\bglucose\b", r"\binsulin\b"],
    "hypertension": [r"\bhigh blood pressure\b", r"\bhyperten(sion|sive)\b", r"\belevated bp\b"],
    "anemia": [r"\banemia\b", r"\banemic\b", r"\blow iron\b", r"\blow hemoglobin\b"],
    "constipation": [r"\bconstipat(ed|ion)\b", r"\birregular bowel\b", r"\bhard stool\b"],
    "heart_disease": [r"\bheart\b", r"\bcardiovascular\b", r"\bcoronary\b", r"\bcholesterol\b", r"\blipid\b"],
    "obesity": [r"\bobesi(ty|e)\b", r"\boverweight\b", r"\bweight loss\b", r"\bweight management\b", r"\bbmi\b"],
    "inflammation": [r"\binflammat(ion|ory)\b", r"\barthriti(s|c)\b", r"\bgout\b", r"\bjoint pain\b"],
    "digestive_issues": [r"\bindigestion\b", r"\bbloating\b", r"\bibs\b", r"\birritable bowel\b", r"\bacid reflux\b", r"\bgerd\b"],
    "immune_support": [r"\bimmuni(ty|e)\b", r"\bfrequent cold\b", r"\bget sick\b", r"\binfection\b"],
    "bone_health": [r"\bosteo(porosis|penia)\b", r"\bweak bones\b", r"\bbone density\b", r"\bcalcium\b"],
    "kidney_health": [r"\bkidney\b", r"\brenal\b", r"\bkidney stone\b"],
    "liver_health": [r"\bliver\b", r"\bfatty liver\b", r"\bhepatic\b", r"\bliver detox\b"],
    "anxiety": [r"\banxiety\b", r"\bstress\b", r"\bdepress(ed|ion)\b", r"\bmood\b", r"\bmental health\b", r"\bbrain fog\b", r"\bmemory\b"],
    "skin_health": [r"\bskin\b", r"\bacne\b", r"\beczema\b", r"\bwrinkle\b", r"\bdry skin\b"],
    "pregnancy": [r"\bpregnan(t|cy)\b", r"\bprenatal\b", r"\bbreastfeeding\b", r"\blactation\b"],
    "eye_health": [r"\beye\b", r"\bvision\b", r"\beyesight\b", r"\bcataract\b"],
}


def extract_diseases(text: str) -> List[str]:
    found = set()
    for disease, patterns in DISEASE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found.add(disease)
                break
    return sorted(found)


def extract_all_entities(text: str) -> Dict[str, List[str]]:
    entities = {
        "diseases": extract_diseases(text),
    }
    text_lower = text.lower()

    fruit_names_path = Path(__file__).resolve().parent.parent.parent / "ml" / "metadata.json"
    try:
        with open(fruit_names_path, "r") as f:
            meta = json.load(f)
            all_fruits = meta.get("classes", [])
            found_fruits = []
            for fruit in all_fruits:
                if fruit.lower() in text_lower or fruit.lower().rstrip("s") in text_lower:
                    found_fruits.append(fruit)
            entities["fruits"] = found_fruits
    except Exception:
        entities["fruits"] = []

    quantity_patterns = [
        (r"\b(\d+)\s*(grams|g|oz|cups?|servings?|pieces?|tbsp|tsp|ml|liters?)\b", "measurement"),
        (r"\bhow much\b", "query"),
        (r"\bhow many\b", "query"),
        (r"\bserving\b", "serving"),
    ]
    entities["quantities"] = []
    for pat, label in quantity_patterns:
        matches = re.findall(pat, text_lower)
        if matches:
            entities["quantities"].extend(matches if isinstance(matches[0], tuple) else [(m, label) for m in matches])

    entities["symptoms"] = []
    symptom_patterns = [
        r"\bfatigue\b", r"\bweakness\b", r"\bdizziness\b", r"\bheadache\b",
        r"\bnausea\b", r"\bpain\b", r"\binflammation\b", r"\bswelling\b",
    ]
    for pat in symptom_patterns:
        if re.search(pat, text_lower):
            entities["symptoms"].append(pat.strip("\\b"))

    return entities


if __name__ == "__main__":
    test_inputs = [
        "I have diabetes and high blood pressure, feeling fatigued",
        "What fruits are good for heart health and cholesterol?",
        "I'm pregnant and need iron-rich fruits",
        "My joints are inflamed, I have arthritis",
    ]
    for inp in test_inputs:
        print(f"Input: {inp}")
        print(f"Entities: {extract_all_entities(inp)}\n")
