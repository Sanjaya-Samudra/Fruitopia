"""Health platform integration layer for wearables and third-party health APIs."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

FILE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = FILE_DIR / "data"

# Simulated health platform integrations
# In production, replace with actual OAuth + API calls


class HealthPlatform:
    """Integration layer for wearable health devices and health data platforms."""

    PLATFORMS = {
        "apple_health": {
            "name": "Apple Health",
            "data_types": ["steps", "heart_rate", "active_energy", "sleep", "dietary_fruit"],
            "icon": "apple_health.png",
            "oauth_url": "https://appleid.apple.com/auth/authorize",
        },
        "google_fit": {
            "name": "Google Fit",
            "data_types": ["steps", "heart_rate", "calories", "sleep", "nutrition"],
            "icon": "google_fit.png",
            "oauth_url": "https://accounts.google.com/o/oauth2/auth",
        },
        "fitbit": {
            "name": "Fitbit",
            "data_types": ["steps", "heart_rate", "sleep", "food_log", "weight"],
            "icon": "fitbit.png",
            "oauth_url": "https://www.fitbit.com/oauth2/authorize",
        },
        "garmin": {
            "name": "Garmin Health",
            "data_types": ["steps", "heart_rate", "stress", "sleep", "body_battery"],
            "icon": "garmin.png",
            "oauth_url": "https://connect.garmin.com/oauth/authorize",
        },
        "whoop": {
            "name": "Whoop",
            "data_types": ["heart_rate", "strain", "recovery", "sleep"],
            "icon": "whoop.png",
            "oauth_url": "https://api.whoop.com/oauth/authorize",
        },
        "oura": {
            "name": "Oura Ring",
            "data_types": ["heart_rate", "hrv", "sleep", "temperature", "activity"],
            "icon": "oura.png",
            "oauth_url": "https://cloud.ouraring.com/oauth/authorize",
        },
    }

    # Correlation rules: fruit nutrients → health metrics
    NUTRIENT_TO_METRIC_CORRELATIONS = {
        "potassium_mg": {"blood_pressure": -0.15, "heart_rate_variability": 0.08},
        "vitamin_c_mg": {"hrv": 0.12, "inflammation_marker": -0.18},
        "fiber_g": {"blood_glucose": -0.20, "digestion_score": 0.25},
        "magnesium_mg": {"sleep_quality": 0.22, "stress_level": -0.18},
        "iron_mg": {"energy_level": 0.20, "blood_oxygen": 0.10},
        "antioxidants": {"inflammation_marker": -0.25, "recovery_rate": 0.15},
    }

    def __init__(self):
        self.connected_platforms: Dict[str, Dict] = {}
        self._load_simulated_data()

    def _load_simulated_data(self):
        self.simulated_profiles = {
            "athlete": {
                "steps": 12000, "heart_rate": 58, "hrv": 72, "sleep_hours": 7.8,
                "stress_level": 32, "recovery_score": 85, "energy_level": 90,
                "blood_pressure": "118/76", "blood_glucose": 85, "inflammation": 22,
            },
            "office_worker": {
                "steps": 4500, "heart_rate": 72, "hrv": 45, "sleep_hours": 6.2,
                "stress_level": 68, "recovery_score": 55, "energy_level": 50,
                "blood_pressure": "128/82", "blood_glucose": 95, "inflammation": 40,
            },
            "senior": {
                "steps": 3800, "heart_rate": 68, "hrv": 35, "sleep_hours": 5.5,
                "stress_level": 45, "recovery_score": 60, "energy_level": 55,
                "blood_pressure": "135/85", "blood_glucose": 105, "inflammation": 50,
            },
        }

    def list_available_platforms(self) -> List[Dict]:
        return [
            {"id": pid, **info}
            for pid, info in self.PLATFORMS.items()
        ]

    def connect_platform(self, platform_id: str, auth_code: str = None, profile_type: str = None) -> Dict:
        if platform_id not in self.PLATFORMS:
            return {"status": "error", "message": f"Platform '{platform_id}' not supported"}

        profile_type = profile_type or "office_worker"
        simulated_data = self.simulated_profiles.get(profile_type, self.simulated_profiles["office_worker"])

        self.connected_platforms[platform_id] = {
            "platform_id": platform_id,
            "connected_at": datetime.now().isoformat(),
            "last_sync": datetime.now().isoformat(),
            "profile_type": profile_type,
            "metrics": simulated_data,
            "access_token": f"tok_{platform_id}_{datetime.now().timestamp()}",
            "data_types": self.PLATFORMS[platform_id]["data_types"],
        }

        return {
            "status": "connected",
            "platform": self.PLATFORMS[platform_id]["name"],
            "profile_type": profile_type,
            "metrics_count": len(simulated_data),
            "last_sync": self.connected_platforms[platform_id]["last_sync"],
        }

    def disconnect_platform(self, platform_id: str) -> Dict:
        if platform_id in self.connected_platforms:
            del self.connected_platforms[platform_id]
            return {"status": "disconnected", "platform_id": platform_id}
        return {"status": "error", "message": "Platform not connected"}

    def get_health_metrics(self, platform_id: str = None) -> Dict:
        if platform_id:
            data = self.connected_platforms.get(platform_id)
            if not data:
                return {"status": "error", "message": "Platform not connected"}
            return data["metrics"]
        # Aggregate all
        all_metrics = {}
        for pid, data in self.connected_platforms.items():
            for k, v in data.get("metrics", {}).items():
                if k not in all_metrics:
                    all_metrics[k] = []
                all_metrics[k].append(v)
        avg_metrics = {}
        for k, vals in all_metrics.items():
            if isinstance(vals[0], str) and "/" in vals[0]:
                avg_metrics[k] = vals[0]
            else:
                avg_metrics[k] = round(sum(vals) / len(vals), 1) if vals else 0
        return avg_metrics

    def get_fruit_recommendations_from_health_data(self, platform_id: str, fruits_db: Dict[str, dict]) -> List[Dict]:
        metrics = self.get_health_metrics(platform_id)
        if isinstance(metrics, dict) and metrics.get("status") == "error":
            return []

        scores = {}
        for fruit_name, fruit_data in fruits_db.items():
            score = 50
            nutrition = fruit_data.get("nutrition", {})
        # Match metrics to nutrients
            for nutrient, correlations in self.NUTRIENT_TO_METRIC_CORRELATIONS.items():
                fruit_val = nutrition.get(nutrient, 0)
                if fruit_val > 0:
                    for metric, corr in correlations.items():
                        if metric == "blood_pressure" and metrics.get("blood_pressure"):
                            try:
                                systolic = int(str(metrics["blood_pressure"]).split("/")[0])
                                if systolic > 130 and corr < 0:
                                    score += abs(corr) * 15
                                elif systolic < 110 and corr < 0:
                                    score -= abs(corr) * 5
                            except Exception:
                                pass
                        elif metric in metrics:
                            metric_val = metrics[metric]
                            if isinstance(metric_val, (int, float)):
                                if (corr > 0 and metric_val < 50) or (corr < 0 and metric_val > 70):
                                    score += abs(corr) * 20
            scores[fruit_name] = round(min(100, max(0, score)), 1)

        sorted_fruits = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {"fruit": name, "match_score": score}
            for name, score in sorted_fruits[:10]
        ]

    def analyze_health_trend(self, platform_id: str, days: int = 30, fruit_intake: List[str] = None) -> Dict:
        metrics = self.get_health_metrics(platform_id)
        if isinstance(metrics, dict) and metrics.get("status") == "error":
            return {"error": "Platform not connected"}

        fruit_intake = fruit_intake or []
        nutrient_summary = {}
        for fruit in fruit_intake:
            pass

        return {
            "period": f"Last {days} days",
            "current_metrics": metrics,
            "fruit_intake_count": len(fruit_intake),
            "estimated_improvements": {
                "energy_level": min(100, metrics.get("energy_level", 50) + len(fruit_intake) * 0.5),
                "digestion_score": min(100, (metrics.get("recovery_score", 60) or 60) + len(fruit_intake) * 0.3),
            },
            "recommendations": [
                "Increase fruit variety for broader nutrient profile",
                "Add fiber-rich fruits for digestive health",
                "Include vitamin C fruits for immune support",
            ],
        }

    def get_sync_status(self) -> Dict:
        return {
            "connected_platforms": list(self.connected_platforms.keys()),
            "last_sync": max(
                (d["last_sync"] for d in self.connected_platforms.values()),
                default=None,
            ),
            "total_metrics": sum(
                len(d.get("metrics", {})) for d in self.connected_platforms.values()
            ),
            "sync_interval_minutes": 15,
        }


health_platform = HealthPlatform()
