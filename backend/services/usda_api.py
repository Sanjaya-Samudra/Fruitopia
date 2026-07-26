import os
import json
import requests
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta

API_KEY = os.environ.get("USDA_API_KEY", "")
BASE_URL = "https://api.nal.usda.gov/fdc/v1"
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "usda_cache"
CACHE_TTL_HOURS = 168

os.makedirs(CACHE_DIR, exist_ok=True)


class USDACache:
    def __init__(self):
        self.cache_dir = CACHE_DIR

    def _cache_path(self, key: str) -> Path:
        safe = key.replace(" ", "_").lower()
        return self.cache_dir / f"{safe}.json"

    def get(self, key: str) -> Optional[dict]:
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            with open(path, "r") as f:
                data = json.load(f)
            cached_time = datetime.fromisoformat(data.get("_cached_at", "2000-01-01"))
            if datetime.now() - cached_time > timedelta(hours=CACHE_TTL_HOURS):
                return None
            return data.get("result")
        except Exception:
            return None

    def set(self, key: str, result: dict):
        path = self._cache_path(key)
        try:
            with open(path, "w") as f:
                json.dump({"_cached_at": datetime.now().isoformat(), "result": result}, f, indent=2)
        except Exception:
            pass


cache = USDACache()


class USDAFoodDataCentral:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = BASE_URL
        self.cache = cache

    def search_foods(self, query: str, page_size: int = 25, page_number: int = 1) -> Dict:
        cache_key = f"search_{query.lower()}_{page_size}_{page_number}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        url = f"{self.base_url}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": page_size,
            "pageNumber": page_number,
            "dataType": ["Foundation", "SR Legacy", "Branded"],
            "sortBy": "dataType.keyword",
            "sortOrder": "asc",
        }
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            self.cache.set(cache_key, data)
            return data
        except requests.RequestException as e:
            return {"error": str(e), "totalHits": 0, "foods": []}

    def get_food_detail(self, fdc_id: int) -> Dict:
        cache_key = f"detail_{fdc_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        url = f"{self.base_url}/food/{fdc_id}"
        params = {"api_key": self.api_key}
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            self.cache.set(cache_key, data)
            return data
        except requests.RequestException as e:
            return {"error": str(e)}

    def search_by_fruit_name(self, fruit_name: str) -> Dict:
        cache_key = f"fruit_{fruit_name.lower()}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        result = self.search_foods(fruit_name, page_size=5)
        if "foods" in result and result["foods"]:
            primary = result["foods"][0]
            fdc_id = primary.get("fdcId")
            if fdc_id:
                detail = self.get_food_detail(fdc_id)
                combined = {
                    "fruit": fruit_name,
                    "search_summary": primary,
                    "detail": detail,
                    "source": "USDA FoodData Central",
                    "cached_at": datetime.now().isoformat(),
                }
                self.cache.set(cache_key, combined)
                return combined
        return {"fruit": fruit_name, "error": "Not found in USDA database", "source": "USDA"}

    def get_nutrient_string(self, nutrients: List[Dict], nutrient_id: int, unit: str = "g") -> str:
        for n in nutrients:
            if n.get("nutrientId") == nutrient_id:
                val = n.get("value", 0)
                return f"{val:.1f} {unit}"
        return f"0 {unit}"

    def extract_nutrition_from_food(self, food_data: Dict) -> Optional[Dict]:
        try:
            food = food_data.get("detail", {}) if "detail" in food_data else food_data
            nutrients = food.get("foodNutrients", [])

            nid_map = {
                "calories": 1008, "protein": 1003, "fat": 1004,
                "carbs": 1005, "fiber": 1079, "sugar": 2000,
                "vitamin_c": 1162, "vitamin_a": 1106, "vitamin_e": 1214,
                "vitamin_k": 1185, "vitamin_d": 1114,
                "calcium": 1087, "iron": 1089, "magnesium": 1090,
                "potassium": 1092, "sodium": 1093, "zinc": 1095,
                "water": 1051,
            }

            result = {}
            for name, nid in nid_map.items():
                for n in nutrients:
                    if n.get("nutrientId") == nid:
                        result[name] = {
                            "value": n.get("value", 0),
                            "unit": n.get("unitName", "g"),
                        }
                        break

            return result if result else None
        except Exception:
            return None


usda_client = USDAFoodDataCentral()
