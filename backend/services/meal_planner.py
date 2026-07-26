"""Intelligent meal planning engine using nutritional optimization."""

import json, random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

FILE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = FILE_DIR.parent
EXPLORE_DIR = PROJECT_ROOT / "data" / "explore"


class MealPlanner:
    """Creates optimized meal plans based on user preferences and nutritional goals."""

    MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]
    GOAL_NUTRIENT_MAP = {
        "weight_loss": {"calories_kcal": -0.3, "fiber_g": 0.2, "protein_g": 0.15},
        "weight_gain": {"calories_kcal": 0.3, "protein_g": 0.2, "carbs_g": 0.2},
        "muscle_build": {"protein_g": 0.3, "calories_kcal": 0.2, "carbs_g": 0.15},
        "energy_boost": {"calories_kcal": 0.2, "carbs_g": 0.25, "vitamin_c_mg": 0.15},
        "immunity": {"vitamin_c_mg": 0.3, "vitamin_a_iu": 0.2, "fiber_g": 0.1},
        "heart_health": {"fiber_g": 0.2, "potassium_mg": 0.2, "fat_g": -0.2},
        "digestion": {"fiber_g": 0.3, "water_percent": 0.15},
        "detox": {"fiber_g": 0.2, "water_percent": 0.2, "vitamin_c_mg": 0.15},
    }

    DISEASE_NUTRIENT_MAP = {
        "diabetes": {"sugar_g": -0.4, "fiber_g": 0.3, "calories_kcal": -0.2},
        "heart_disease": {"fat_g": -0.3, "fiber_g": 0.2, "potassium_mg": 0.2},
        "hypertension": {"potassium_mg": 0.3, "sodium_mg": -0.4},
        "anemia": {"iron_mg": 0.3, "vitamin_c_mg": 0.25},
        "obesity": {"calories_kcal": -0.3, "fiber_g": 0.25, "sugar_g": -0.2},
        "inflammation": {"vitamin_c_mg": 0.2, "fiber_g": 0.15},
    }

    RECIPE_TEMPLATES = {
        "breakfast": [
            {"name": "{fruit} Smoothie Bowl", "type": "smoothie", "time": "10 min"},
            {"name": "{fruit} & Oatmeal", "type": "bowl", "time": "15 min"},
            {"name": "{fruit} Yogurt Parfait", "type": "parfait", "time": "5 min"},
            {"name": "Toasted {fruit} & Granola", "type": "toast", "time": "10 min"},
        ],
        "lunch": [
            {"name": "{fruit} & Quinoa Salad", "type": "salad", "time": "20 min"},
            {"name": "{fruit} Wrap", "type": "wrap", "time": "15 min"},
            {"name": "{fruit} & Grain Bowl", "type": "bowl", "time": "25 min"},
            {"name": "Mediterranean {fruit} Salad", "type": "salad", "time": "15 min"},
        ],
        "dinner": [
            {"name": "Grilled {fruit} & Vegetables", "type": "grill", "time": "30 min"},
            {"name": "{fruit} Stir-Fry", "type": "stir-fry", "time": "20 min"},
            {"name": "Stuffed {fruit} with Rice", "type": "stuffed", "time": "35 min"},
            {"name": "{fruit} Curry", "type": "curry", "time": "30 min"},
        ],
        "snack": [
            {"name": "Fresh {fruit} Slices", "type": "raw", "time": "2 min"},
            {"name": "{fruit} Energy Balls", "type": "no-bake", "time": "15 min"},
            {"name": "{fruit} & Nut Butter", "type": "spread", "time": "3 min"},
            {"name": "Frozen {fruit} Bites", "type": "frozen", "time": "5 min"},
        ],
    }

    def __init__(self):
        self.fruits_db: Dict[str, dict] = {}
        self._load_fruits()

    def _load_fruits(self):
        if not EXPLORE_DIR.exists():
            return
        for json_file in EXPLORE_DIR.glob("*.json"):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
                name = data.get("fruitName", json_file.stem).lower()
                nutrition = data.get("nutritionalFacts", {})
                macros = nutrition.get("macronutrients", {})
                self.fruits_db[name] = {
                    "name": name,
                    "display_name": data.get("fruitName", name),
                    "calories_kcal": nutrition.get("calories_kcal", 0),
                    "protein_g": macros.get("protein_g", 0),
                    "carbs_g": macros.get("carbohydrates_g", macros.get("carbs_g", 0)),
                    "fat_g": macros.get("fat_g", 0),
                    "fiber_g": macros.get("fiber_g", 0),
                    "sugar_g": macros.get("sugar_g", 0),
                    "vitamin_c_mg": nutrition.get("vitamin_c_mg", 0),
                    "vitamin_a_iu": nutrition.get("vitamin_a_iu", 0),
                    "potassium_mg": nutrition.get("potassium_mg", 0),
                    "iron_mg": nutrition.get("iron_mg", 0),
                    "water_percent": nutrition.get("waterContent_percent", 80),
                    "serving_size": nutrition.get("servingSize_g", 100),
                    "health_benefits": data.get("healthBenefits", [])[:3],
                    "colors": (data.get("appearance", {}) or {}).get("colors", ["green"]),
                    "season": (data.get("storageAndShelfLife", {}) or {}).get("seasonAvailability", "Year-round"),
                    "pairings": (data.get("culinaryInformation", {}) or {}).get("pairings", []),
                }
            except Exception:
                pass

    def get_all_fruits(self) -> List[dict]:
        return list(self.fruits_db.values())

    def generate_meal_plan(
        self,
        days: int = 7,
        goals: List[str] = None,
        diseases: List[str] = None,
        dietary_prefs: List[str] = None,
        available_fruits: List[str] = None,
        meals_per_day: List[str] = None,
        calories_target: int = None,
    ) -> Dict:
        goals = goals or []
        diseases = diseases or []
        dietary_prefs = [p.lower() for p in (dietary_prefs or [])]
        available_fruits = [f.lower() for f in (available_fruits or [])]
        meals_per_day = meals_per_day or ["breakfast", "lunch", "dinner", "snack"]

        fruits = self.get_all_fruits()
        if available_fruits:
            fruits = [f for f in fruits if f["name"] in available_fruits]
        if not fruits:
            fruits = self.get_all_fruits()

        scoring_weights = self._compute_weights(goals, diseases, dietary_prefs)
        scored_fruits = self._score_fruits(fruits, scoring_weights)
        top_fruits = [f["name"] for f in scored_fruits[:10]]

        start_date = datetime.now()
        plan = {"days": [], "meal_types": meals_per_day, "start_date": start_date.isoformat()}

        for day in range(days):
            date = (start_date + timedelta(days=day)).strftime("%A, %b %d")
            day_fruits = self._select_daily_fruits(top_fruits, day, len(meals_per_day))
            total_nutrition = {"calories_kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fiber_g": 0}
            meals = []

            for i, meal_type in enumerate(meals_per_day):
                fruit = day_fruits[i % len(day_fruits)]
                fruit_data = self.fruits_db.get(fruit, {})
                recipe = self._generate_recipe(fruit_data, meal_type)

                nutrition = {
                    "calories_kcal": fruit_data.get("calories_kcal", 0),
                    "protein_g": fruit_data.get("protein_g", 0),
                    "carbs_g": fruit_data.get("carbs_g", 0),
                    "fat_g": fruit_data.get("fat_g", 0),
                    "fiber_g": fruit_data.get("fiber_g", 0),
                }
                for k in total_nutrition:
                    total_nutrition[k] += nutrition.get(k, 0)

                meals.append({
                    "type": meal_type,
                    "fruit": fruit_data.get("display_name", fruit),
                    "recipe": recipe,
                    "nutrition": nutrition,
                    "benefits": fruit_data.get("health_benefits", [])[:2],
                    "color": (fruit_data.get("colors") or ["green"])[0],
                })

            plan["days"].append({
                "date": date,
                "meals": meals,
                "total_nutrition": total_nutrition,
            })

        avg_nutrition = {}
        for k in total_nutrition:
            avg_nutrition[k] = round(total_nutrition[k] / days, 1)

        plan["summary"] = {
            "total_days": days,
            "average_daily_nutrition": avg_nutrition,
            "goals": goals,
            "diseases_considered": diseases,
            "dietary_preferences": dietary_prefs,
            "scoring_weights": {k: round(v, 3) for k, v in scoring_weights.items() if abs(v) > 0.01},
        }

        return plan

    def _compute_weights(self, goals: List[str], diseases: List[str], dietary_prefs: List[str]) -> Dict[str, float]:
        weights = {
            "calories_kcal": 0, "protein_g": 0, "carbs_g": 0,
            "fat_g": 0, "fiber_g": 0, "sugar_g": 0,
            "vitamin_c_mg": 0, "potassium_mg": 0, "iron_mg": 0,
            "water_percent": 0,
        }

        for goal in goals:
            if goal in self.GOAL_NUTRIENT_MAP:
                for nutrient, weight in self.GOAL_NUTRIENT_MAP[goal].items():
                    if nutrient in weights:
                        weights[nutrient] += weight

        for disease in diseases:
            if disease in self.DISEASE_NUTRIENT_MAP:
                for nutrient, weight in self.DISEASE_NUTRIENT_MAP[disease].items():
                    if nutrient in weights:
                        weights[nutrient] += weight

        if "vegan" in dietary_prefs:
            weights["protein_g"] += 0.15
            weights["fiber_g"] += 0.1
        if "low_carb" in dietary_prefs:
            weights["carbs_g"] -= 0.3
            weights["protein_g"] += 0.2
        if "high_protein" in dietary_prefs:
            weights["protein_g"] += 0.3
        if "low_sugar" in dietary_prefs:
            weights["sugar_g"] -= 0.3
            weights["fiber_g"] += 0.1
        if "gluten_free" in dietary_prefs:
            pass
        if "keto" in dietary_prefs:
            weights["carbs_g"] -= 0.4
            weights["fat_g"] += 0.2
            weights["protein_g"] += 0.15

        return weights

    def _score_fruits(self, fruits: List[dict], weights: Dict[str, float]) -> List[dict]:
        scored = []
        for fruit in fruits:
            score = 0
            for nutrient, weight in weights.items():
                val = fruit.get(nutrient, 0)
                max_val = max(f.get(nutrient, 0) for f in fruits) or 1
                normalized = val / max_val
                score += normalized * weight
            scored.append({**fruit, "score": round(score, 4)})
        return sorted(scored, key=lambda x: x["score"], reverse=True)

    def _select_daily_fruits(self, top_fruits: List[str], day: int, meals_count: int) -> List[str]:
        random.seed(42 + day)
        needed = max(meals_count, 3)
        selected = []
        available = list(top_fruits)
        for _ in range(needed):
            if not available:
                available = list(top_fruits)
            choice = random.choice(available)
            selected.append(choice)
            available.remove(choice)
            if len(available) < 2:
                available = [f for f in top_fruits if f not in selected[-3:]]
        return selected

    def _generate_recipe(self, fruit_data: dict, meal_type: str) -> Dict:
        templates = self.RECIPE_TEMPLATES.get(meal_type, self.RECIPE_TEMPLATES["snack"])
        template = random.choice(templates)
        name = fruit_data.get("display_name", "fruit") or "fruit"
        title = template["name"].format(fruit=name)

        return {
            "title": title,
            "type": template["type"],
            "prep_time": template["time"],
            "ingredients": [f"{name.title()}", f"1 {fruit_data.get('serving_size', 100)}g serving"],
            "difficulty": "easy",
        }

    def generate_shopping_list(self, meal_plan: Dict) -> List[Dict]:
        fruits_needed = {}
        for day in meal_plan.get("days", []):
            for meal in day.get("meals", []):
                fruit = meal.get("fruit", "").lower()
                fruits_needed[fruit] = fruits_needed.get(fruit, 0) + 1

        shopping = []
        for fruit, count in sorted(fruits_needed.items()):
            fruit_data = self.fruits_db.get(fruit, {})
            shopping.append({
                "fruit": fruit_data.get("display_name", fruit),
                "quantity": count,
                "unit": "servings",
                "season": fruit_data.get("season", "Year-round"),
                "color": (fruit_data.get("colors") or ["green"])[0],
            })
        return shopping


meal_planner = MealPlanner()
