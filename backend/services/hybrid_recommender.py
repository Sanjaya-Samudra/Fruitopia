"""Hybrid ML Recommender System with content-based + collaborative filtering."""

import json, math, random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import numpy as np

FILE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = FILE_DIR.parent
EXPLORE_DIR = PROJECT_ROOT / "data" / "explore"


class NutritionalVectorizer:
    """Converts fruit nutritional data into feature vectors for similarity computation."""

    NUTRIENT_KEYS = [
        "calories_kcal", "fiber_g", "sugar_g", "protein_g", "fat_g",
        "vitamin_c_mg", "vitamin_a_iu", "calcium_mg", "iron_mg",
        "potassium_mg", "magnesium_mg", "water_percent",
    ]

    def __init__(self):
        self.fruit_vectors: Dict[str, np.ndarray] = {}
        self.fruit_names: List[str] = []
        self._build_vectors()

    def _build_vectors(self):
        if not EXPLORE_DIR.exists():
            return
        vectors = []
        names = []
        for json_file in sorted(EXPLORE_DIR.glob("*.json")):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
                name = data.get("fruitName", json_file.stem).lower()
                nutrition = data.get("nutritionalFacts", {})
                vec = self._extract_vector(nutrition)
                vectors.append(vec)
                names.append(name)
            except Exception:
                pass
        if vectors:
            arr = np.array(vectors)
            self.fruit_vectors = {n: arr[i] for i, n in enumerate(names)}
            self.fruit_names = names
            self._similarity_matrix = self._compute_similarity_matrix(arr)

    def _extract_vector(self, nutrition: Dict) -> np.ndarray:
        vec = []
        macros = nutrition.get("macronutrients", {})
        for key in self.NUTRIENT_KEYS:
            if key in macros:
                vec.append(float(macros[key]))
            elif key in nutrition:
                vec.append(float(nutrition[key]))
            else:
                vec.append(0.0)
        arr = np.array(vec)
        norm = np.linalg.norm(arr)
        return arr / norm if norm > 0 else arr

    def _compute_similarity_matrix(self, arr: np.ndarray) -> np.ndarray:
        norm = arr / (np.linalg.norm(arr, axis=1, keepdims=True) + 1e-8)
        return np.dot(norm, norm.T)

    def get_similar_fruits(self, fruit_name: str, k: int = 5) -> List[Tuple[str, float]]:
        fruit_name = fruit_name.lower()
        if fruit_name not in self.fruit_vectors:
            return []
        idx = self.fruit_names.index(fruit_name)
        sims = self._similarity_matrix[idx]
        top_indices = np.argsort(sims)[::-1][1:k + 1]
        return [(self.fruit_names[i], float(sims[i])) for i in top_indices]

    def vectorize_health_profile(self, diseases: List[str], preferences: Dict = None) -> Optional[np.ndarray]:
        """Create a user health profile vector based on diseases and preferences."""
        disease_nutrient_profiles = {
            "diabetes": {"fiber_g": 1.0, "sugar_g": -1.0, "calories_kcal": -0.5},
            "heart_disease": {"fiber_g": 1.0, "fat_g": -0.8, "potassium_mg": 0.8},
            "hypertension": {"potassium_mg": 1.0, "sodium_mg": -1.0 if "sodium_mg" in self.NUTRIENT_KEYS else 0},
            "anemia": {"iron_mg": 1.0, "vitamin_c_mg": 1.0},
            "inflammation": {"vitamin_c_mg": 0.8, "fiber_g": 0.5},
            "obesity": {"calories_kcal": -1.0, "fiber_g": 1.0, "sugar_g": -0.8},
            "immune_support": {"vitamin_c_mg": 1.0, "vitamin_a_iu": 0.7},
            "digestive_issues": {"fiber_g": 1.0},
            "bone_health": {"calcium_mg": 1.0, "magnesium_mg": 0.8},
            "skin_health": {"vitamin_c_mg": 1.0, "vitamin_a_iu": 0.6},
            "eye_health": {"vitamin_a_iu": 1.0, "vitamin_c_mg": 0.5},
            "pregnancy": {"folate_µg": 1.0, "iron_mg": 0.8},
            "liver_health": {"vitamin_c_mg": 0.7, "fiber_g": 0.6},
        }
        profile = np.zeros(len(self.NUTRIENT_KEYS))
        count = 0
        for disease in diseases:
            profile_map = disease_nutrient_profiles.get(disease, {})
            for key, direction in profile_map.items():
                if key in self.NUTRIENT_KEYS:
                    idx = self.NUTRIENT_KEYS.index(key)
                    profile[idx] += direction
                    count += 1
        if preferences:
            if preferences.get("high_protein"):
                profile[self.NUTRIENT_KEYS.index("protein_g")] += 0.5
            if preferences.get("low_sugar"):
                profile[self.NUTRIENT_KEYS.index("sugar_g")] -= 0.8
            if preferences.get("low_calorie"):
                profile[self.NUTRIENT_KEYS.index("calories_kcal")] -= 0.8
        norm = np.linalg.norm(profile)
        return profile / norm if norm > 0 else None

    def score_fruits_for_profile(self, profile: np.ndarray, top_k: int = 10) -> List[Tuple[str, float]]:
        """Score all fruits against a user health profile vector."""
        scores = []
        for name in self.fruit_names:
            vec = self.fruit_vectors[name]
            sim = float(np.dot(profile, vec))
            scores.append((name, sim))
        return sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]


class UserPreferenceModel:
    """Simple collaborative filtering model using user feedback scoring."""

    def __init__(self):
        self.user_preferences: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.session_fruits: Dict[str, List[str]] = defaultdict(list)

    def record_interaction(self, user_id: str, fruit: str, rating: float = 1.0):
        self.user_preferences[user_id][fruit] += rating
        if fruit not in self.session_fruits[user_id]:
            self.session_fruits[user_id].append(fruit)

    def get_user_affinity(self, user_id: str) -> Dict[str, float]:
        return dict(self.user_preferences.get(user_id, {}))

    def get_session_fruits(self, user_id: str) -> List[str]:
        return self.session_fruits.get(user_id, [])

    def score_fruit_for_user(self, user_id: str, fruit: str, nutritional_similarity: float = 0) -> float:
        prefs = self.user_preferences.get(user_id, {})
        history_score = prefs.get(fruit, 0)
        return 0.7 * nutritional_similarity + 0.3 * (1 / (1 + math.exp(-history_score)))


class DiversityRanker:
    """Ensures recommendation diversity by penalizing similar fruits."""

    def __init__(self, vectorizer: NutritionalVectorizer):
        self.vectorizer = vectorizer
        self.similarity_penalty = 0.3

    def diversify(self, candidates: List[Tuple[str, float]], top_k: int = 5) -> List[Tuple[str, float, float]]:
        if not candidates:
            return []
        selected = []
        remaining = list(candidates)
        first = remaining.pop(0)
        selected.append((first[0], first[1], first[1]))

        while len(selected) < top_k and remaining:
            best_score = -float("inf")
            best_idx = -1
            for i, (name, score) in enumerate(remaining):
                penalty = 0
                for sel_name, _, _ in selected:
                    sims = self.vectorizer.get_similar_fruits(sel_name, k=10)
                    for sim_name, sim_score in sims:
                        if sim_name == name:
                            penalty += sim_score * self.similarity_penalty
                            break
                adjusted = score - penalty
                if adjusted > best_score:
                    best_score = adjusted
                    best_idx = i
            if best_idx >= 0:
                name, score = remaining.pop(best_idx)
                selected.append((name, score, best_score))
        return selected


class HybridRecommender:
    """Main hybrid recommender combining content-based + collaborative + diversity."""

    def __init__(self):
        self.vectorizer = NutritionalVectorizer()
        self.user_model = UserPreferenceModel()
        self.diversity = DiversityRanker(self.vectorizer)
        self._load_disease_recs()

    def _load_disease_recs(self):
        path = FILE_DIR / "ml" / "disease_recs.json"
        try:
            with open(path, "r") as f:
                self.disease_recs = json.load(f)
        except Exception:
            self.disease_recs = {}

    def recommend(
        self,
        user_id: Optional[str] = None,
        diseases: List[str] = None,
        have: List[str] = None,
        preferences: Dict = None,
        top_k: int = 5,
        diversify: bool = True,
    ) -> Dict:
        have = [h.lower() for h in (have or [])]
        diseases = diseases or []
        user_id = user_id or "anonymous"

        candidates: Dict[str, float] = {}

        # 1. Disease-based recommendations (knowledge-driven)
        for disease in diseases:
            recs = self.disease_recs.get(disease, [])
            for r in recs:
                cls = r.get("class", "").lower()
                score = r.get("score", 0.5)
                if cls not in have:
                    candidates[cls] = max(candidates.get(cls, 0), score)

        # 2. Content-based (nutritional profile matching)
        if diseases:
            profile = self.vectorizer.vectorize_health_profile(diseases, preferences)
            if profile is not None:
                content_scores = self.vectorizer.score_fruits_for_profile(profile, top_k=15)
                for name, score in content_scores:
                    if name not in have:
                        candidates[name] = max(candidates.get(name, 0), score * 0.9)

        # 3. Collaborative (user history)
        if user_id and user_id != "anonymous":
            for fruit, affinity in self.user_model.get_user_affinity(user_id).items():
                if fruit not in have:
                    candidates[fruit] = max(candidates.get(fruit, 0), affinity * 1.1)

        # 4. Session-based (add serendipity)
        session_fruits = self.user_model.get_session_fruits(user_id) if user_id else []
        all_fruits = self.vectorizer.fruit_names
        for fruit in all_fruits:
            if fruit not in candidates and fruit not in have and fruit not in session_fruits:
                random_score = random.uniform(0.1, 0.3)
                candidates[fruit] = random_score * 0.3

        # Rank and diversify
        ranked = sorted(candidates.items(), key=lambda x: x[1], reverse=True)

        if diversify and len(ranked) > 1:
            diversified = self.diversity.diversify(ranked, top_k=top_k)
            recommendations = []
            for name, orig_score, adj_score in diversified:
                rec_data = self._get_fruit_rec_data(name)
                rec_data["score"] = round(orig_score, 3)
                rec_data["adjusted_score"] = round(adj_score, 3)
                recommendations.append(rec_data)
        else:
            recommendations = []
            for name, score in ranked[:top_k]:
                rec_data = self._get_fruit_rec_data(name)
                rec_data["score"] = round(score, 3)
                recommendations.append(rec_data)

        return {
            "recommendations": recommendations,
            "signals": {
                "disease_based": bool(diseases),
                "content_based": bool(diseases),
                "collaborative": user_id != "anonymous",
                "serendipity": True,
            },
            "total_candidates": len(candidates),
        }

    def _get_fruit_rec_data(self, name: str) -> Dict:
        data = {"class": name}
        try:
            path = EXPLORE_DIR / f"{name}.json"
            if path.exists():
                with open(path, "r") as f:
                    fruit = json.load(f)
                benefits = fruit.get("healthBenefits", [])
                data["reason"] = benefits[0] if benefits else "Nutrient-rich fruit"
                data["benefits"] = benefits[:3]
                data["calories"] = fruit.get("nutritionalFacts", {}).get("calories_kcal", 0)
                data["color"] = (fruit.get("appearance", {}) or {}).get("colors", ["green"])[0]
        except Exception:
            data["reason"] = "Excellent choice for your health"
        return data

    def record_user_feedback(self, user_id: str, fruit: str, rating: float = 1.0):
        self.user_model.record_interaction(user_id, fruit, rating)


hybrid_recommender = HybridRecommender()
