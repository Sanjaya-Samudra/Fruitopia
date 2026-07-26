import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from difflib import get_close_matches

FILE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = FILE_DIR.parent
EXPLORE_DIR = PROJECT_ROOT / "data" / "explore"
CACHE_DIR = PROJECT_ROOT / "data" / "usda_cache"


class FruitService:
    def __init__(self):
        self._fruits: Dict[str, dict] = {}
        self._load_all()

    def _load_all(self):
        if not EXPLORE_DIR.exists():
            return
        for json_file in sorted(EXPLORE_DIR.glob("*.json")):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                name = data.get("fruitName", "").lower()
                if name:
                    self._fruits[name] = data
            except Exception:
                pass

    def get_all_fruits(self) -> List[dict]:
        return [
            {
                "name": v.get("fruitName", k),
                "slug": k,
                "scientificName": v.get("scientificName", ""),
                "description": v.get("description", "")[:150] + "...",
                "origin": v.get("origin", ""),
                "family": v.get("family", ""),
                "health_benefits": v.get("healthBenefits", [])[:3],
                "fun_facts": v.get("funFacts", [])[:2],
                "colors": v.get("appearance", {}).get("colors", []),
                "season": v.get("storageAndShelfLife", {}).get("seasonAvailability", "Year-round"),
                "calories": v.get("nutritionalFacts", {}).get("calories_kcal", 0),
            }
            for k, v in self._fruits.items()
        ]

    def get_fruit(self, slug: str) -> Optional[dict]:
        slug = slug.lower().replace(" ", "_")
        if slug in self._fruits:
            data = dict(self._fruits[slug])
            return data
        for k, v in self._fruits.items():
            if get_close_matches(slug, [k], n=1, cutoff=0.6):
                return dict(v)
        return None

    def get_fruit_nutrition(self, slug: str) -> Optional[dict]:
        fruit = self.get_fruit(slug)
        if fruit:
            return fruit.get("nutritionalFacts")
        return None

    def get_fruit_health_benefits(self, slug: str) -> List[str]:
        fruit = self.get_fruit(slug)
        if fruit:
            return fruit.get("healthBenefits", [])
        return []

    def search_fruits(self, query: str) -> List[dict]:
        query = query.lower()
        results = []
        for k, v in self._fruits.items():
            score = 0
            if query in k:
                score += 10
            if any(query in benefit.lower() for benefit in v.get("healthBenefits", [])):
                score += 5
            if query in v.get("description", "").lower():
                score += 3
            if any(query in fact.lower() for fact in v.get("funFacts", [])):
                score += 2
            if score > 0:
                results.append({
                    "name": v.get("fruitName", k),
                    "slug": k,
                    "score": score,
                    "description": v.get("description", "")[:200],
                })
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def search_by_benefit(self, benefit: str) -> List[dict]:
        benefit = benefit.lower()
        results = []
        for k, v in self._fruits.items():
            benefits = [b.lower() for b in v.get("healthBenefits", [])]
            if any(benefit in b for b in benefits):
                results.append({
                    "name": v.get("fruitName", k),
                    "slug": k,
                    "description": v.get("description", "")[:200],
                    "matching_benefits": [b for b in v.get("healthBenefits", []) if benefit in b.lower()],
                })
        return results

    def get_fruit_seasonality(self) -> List[dict]:
        results = []
        for k, v in self._fruits.items():
            season = v.get("storageAndShelfLife", {}).get("seasonAvailability", "Year-round")
            results.append({
                "name": v.get("fruitName", k),
                "slug": k,
                "season": season,
                "origin": v.get("origin", ""),
            })
        return results

    def get_fruit_count(self) -> int:
        return len(self._fruits)

    def get_all_slugs(self) -> List[str]:
        return sorted(self._fruits.keys())


fruit_service = FruitService()
