import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from difflib import get_close_matches
import numpy as np

FILE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = FILE_DIR.parent
RECS_FILE = FILE_DIR / "ml" / "disease_recs.json"
SYN_FILE = FILE_DIR / "ml" / "disease_synonyms.json"


def _load_json(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


disease_synonyms: Dict[str, List[str]] = _load_json(SYN_FILE)


DISEASES_EXTENDED = {
    "diabetes": {
        "synonyms": ["high blood sugar", "diabetic", "type 2 diabetes", "type 1 diabetes", "glucose intolerance", "insulin resistance", "hyperglycemia"],
        "severity": "high",
        "category": "metabolic"
    },
    "hypertension": {
        "synonyms": ["high blood pressure", "high bp", "elevated blood pressure", "hypertensive"],
        "severity": "high",
        "category": "cardiovascular"
    },
    "anemia": {
        "synonyms": ["low iron", "iron deficiency", "low hemoglobin", "fatigue", "weakness"],
        "severity": "medium",
        "category": "blood"
    },
    "constipation": {
        "synonyms": ["irregular bowel", "hard stools", "difficulty passing stool", "blocked"],
        "severity": "low",
        "category": "digestive"
    },
    "heart_disease": {
        "synonyms": ["cardiovascular disease", "coronary artery disease", "heart failure", "cardiac", "heart condition", "cholesterol", "high cholesterol", "hyperlipidemia"],
        "severity": "high",
        "category": "cardiovascular"
    },
    "obesity": {
        "synonyms": ["overweight", "weight management", "weight loss", "high bmi", "fatigue"],
        "severity": "medium",
        "category": "metabolic"
    },
    "inflammation": {
        "synonyms": ["arthritis", "joint pain", "swelling", "inflammatory", "rheumatoid", "gout"],
        "severity": "medium",
        "category": "immune"
    },
    "digestive_issues": {
        "synonyms": ["indigestion", "bloating", "gas", "ibs", "irritable bowel", "acid reflux", "gerd", "stomach"],
        "severity": "low",
        "category": "digestive"
    },
    "immune_support": {
        "synonyms": ["weak immune", "frequent cold", "immunity", "infection prone", "low immunity", "get sick often"],
        "severity": "medium",
        "category": "immune"
    },
    "bone_health": {
        "synonyms": ["osteoporosis", "weak bones", "bone density", "fracture prone", "calcium deficiency"],
        "severity": "medium",
        "category": "musculoskeletal"
    },
    "kidney_health": {
        "synonyms": ["kidney disease", "kidney stones", "renal", "chronic kidney"],
        "severity": "high",
        "category": "renal"
    },
    "liver_health": {
        "synonyms": ["fatty liver", "liver disease", "hepatic", "liver detox", "cirrhosis"],
        "severity": "high",
        "category": "hepatic"
    },
    "anxiety": {
        "synonyms": ["stress", "depression", "mood", "mental health", "brain fog", "cognitive decline", "memory"],
        "severity": "medium",
        "category": "neurological"
    },
    "skin_health": {
        "synonyms": ["acne", "skin glow", "dull skin", "aging skin", "wrinkles", "dry skin", "eczema"],
        "severity": "low",
        "category": "dermatological"
    },
    "pregnancy": {
        "synonyms": ["pregnant", "prenatal", "expecting", "maternal health", "breastfeeding", "lactation"],
        "severity": "high",
        "category": "reproductive"
    },
    "eye_health": {
        "synonyms": ["vision", "eyesight", "cataract", "macular degeneration", "night blindness", "glaucoma"],
        "severity": "medium",
        "category": "ophthalmological"
    }
}


def normalize_disease(raw: str) -> Optional[str]:
    raw_lower = raw.strip().lower()
    if not raw_lower:
        return None

    data = _load_json(RECS_FILE)
    if raw_lower in data:
        return raw_lower

    for canon, info in DISEASES_EXTENDED.items():
        if raw_lower == canon or raw_lower in info["synonyms"]:
            return canon

    syn = _load_json(SYN_FILE)
    for canon, vals in syn.items():
        vals_lower = [v.lower() for v in vals]
        if raw_lower in vals_lower:
            return canon

    all_terms = list(data.keys()) + list(DISEASES_EXTENDED.keys())
    for vals in DISEASES_EXTENDED.values():
        all_terms.extend(vals["synonyms"])
    for vals in _load_json(SYN_FILE).values():
        all_terms.extend(v.lower() for v in vals)

    matches = get_close_matches(raw_lower, all_terms, n=1, cutoff=0.55)
    if matches:
        m = matches[0]
        if m in data:
            return m
        if m in DISEASES_EXTENDED:
            return m
        for canon, info in DISEASES_EXTENDED.items():
            if m in info["synonyms"]:
                return canon
        for canon, vals in syn.items():
            if m in [v.lower() for v in vals]:
                return canon
    return "general"


def get_recommendations(
    disease_raw: str,
    have: List[str] = None,
    min_score: float = 0.5,
    max_results: int = 5
) -> Dict:
    have = [h.strip().lower() for h in (have or [])]
    disease_key = normalize_disease(disease_raw)
    if not disease_key:
        return {"recommendations": [], "disease": None, "normalized": None, "category": None}

    data = _load_json(RECS_FILE)
    candidates = data.get(disease_key, [])

    disease_info = DISEASES_EXTENDED.get(disease_key, {})
    category = disease_info.get("category", "general")
    severity = disease_info.get("severity", "medium")

    if not candidates:
        for canon, info in DISEASES_EXTENDED.items():
            if info.get("category") == category and canon in data:
                candidates.extend(data[canon])
        if not candidates:
            candidates = data.get("general", [])

    filtered = [c for c in candidates if c.get("class", "").strip().lower() not in have]
    filtered = [c for c in filtered if c.get("score", 0) >= min_score]
    scored = sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)

    out = []
    for item in scored[:max_results]:
        cls = item.get("class", "").lower()
        sample_file = None
        class_dir = PROJECT_ROOT / "data" / "FruitImageDataset" / cls
        if class_dir.exists() and class_dir.is_dir():
            files = sorted([p.name for p in class_dir.iterdir() if p.is_file()])
            if files:
                sample_file = files[0]
        itm = dict(item)
        if sample_file:
            itm["sample"] = sample_file
        out.append(itm)

    return {
        "recommendations": out,
        "disease": disease_key,
        "normalized": disease_key,
        "category": category,
        "severity": severity,
        "total_candidates": len(candidates),
        "filtered_count": len(filtered),
    }
