"""Premium tier subscription and production configuration management."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

FILE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = FILE_DIR / "data"
CONFIG_DIR = FILE_DIR / "config"

PREMIUM_TIERS = {
    "free": {
        "name": "Free",
        "price_monthly": 0,
        "price_yearly": 0,
        "features": {
            "api_calls_per_day": 100,
            "meal_plans_per_day": 1,
            "max_meal_plan_days": 3,
            "vision_analysis": False,
            "barcode_scanner": False,
            "health_platform_connections": 0,
            "knowledge_graph_access": False,
            "detailed_evidence": False,
            "fruit_culture_data": False,
            "export_feature": False,
            "priority_support": False,
            "ads_enabled": True,
        },
        "rate_limits": {
            "requests_per_minute": 20,
            "requests_per_hour": 200,
        },
    },
    "basic": {
        "name": "Basic",
        "price_monthly": 4.99,
        "price_yearly": 49.99,
        "features": {
            "api_calls_per_day": 1000,
            "meal_plans_per_day": 5,
            "max_meal_plan_days": 7,
            "vision_analysis": True,
            "barcode_scanner": True,
            "health_platform_connections": 1,
            "knowledge_graph_access": True,
            "detailed_evidence": True,
            "fruit_culture_data": False,
            "export_feature": True,
            "priority_support": False,
            "ads_enabled": False,
        },
        "rate_limits": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
        },
    },
    "pro": {
        "name": "Pro",
        "price_monthly": 12.99,
        "price_yearly": 129.99,
        "features": {
            "api_calls_per_day": 10000,
            "meal_plans_per_day": 50,
            "max_meal_plan_days": 30,
            "vision_analysis": True,
            "barcode_scanner": True,
            "health_platform_connections": 5,
            "knowledge_graph_access": True,
            "detailed_evidence": True,
            "fruit_culture_data": True,
            "export_feature": True,
            "priority_support": True,
            "ads_enabled": False,
        },
        "rate_limits": {
            "requests_per_minute": 300,
            "requests_per_hour": 5000,
        },
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 49.99,
        "price_yearly": 499.99,
        "features": {
            "api_calls_per_day": 100000,
            "meal_plans_per_day": 500,
            "max_meal_plan_days": 90,
            "vision_analysis": True,
            "barcode_scanner": True,
            "health_platform_connections": 20,
            "knowledge_graph_access": True,
            "detailed_evidence": True,
            "fruit_culture_data": True,
            "export_feature": True,
            "priority_support": True,
            "ads_enabled": False,
        },
        "rate_limits": {
            "requests_per_minute": 1000,
            "requests_per_hour": 20000,
        },
    },
}


class PremiumManager:
    """Manages subscription tiers, rate limiting, and access control."""

    def __init__(self):
        self.subscribers: Dict[str, Dict] = {}
        self.tiers = PREMIUM_TIERS
        self._usage_counts: Dict[str, Dict] = {}

    def list_tiers(self) -> Dict:
        return {
            tier_id: {
                "name": info["name"],
                "price_monthly": info["price_monthly"],
                "price_yearly": info["price_yearly"],
                "features": info["features"],
            }
            for tier_id, info in self.tiers.items()
        }

    def get_tier(self, tier_id: str) -> Optional[Dict]:
        return self.tiers.get(tier_id)

    def create_subscription(self, user_id: str, tier_id: str, billing_cycle: str = "monthly") -> Dict:
        if tier_id not in self.tiers:
            return {"status": "error", "message": f"Tier '{tier_id}' not found"}

        now = datetime.now()
        if billing_cycle == "yearly":
            expires = now + timedelta(days=365)
        else:
            expires = now + timedelta(days=30)

        subscription = {
            "user_id": user_id,
            "tier": tier_id,
            "tier_name": self.tiers[tier_id]["name"],
            "billing_cycle": billing_cycle,
            "started_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "active": True,
            "auto_renew": True,
            "features": self.tiers[tier_id]["features"],
            "rate_limits": self.tiers[tier_id]["rate_limits"],
        }

        self.subscribers[user_id] = subscription
        return {"status": "active", "subscription": subscription}

    def cancel_subscription(self, user_id: str) -> Dict:
        if user_id in self.subscribers:
            self.subscribers[user_id]["active"] = False
            self.subscribers[user_id]["auto_renew"] = False
            return {"status": "cancelled", "expires_at": self.subscribers[user_id]["expires_at"]}
        return {"status": "error", "message": "No active subscription"}

    def upgrade_subscription(self, user_id: str, new_tier: str, billing_cycle: str = None) -> Dict:
        if user_id not in self.subscribers:
            return self.create_subscription(user_id, new_tier, billing_cycle or "monthly")
        if new_tier not in self.tiers:
            return {"status": "error", "message": f"Tier '{new_tier}' not found"}

        self.subscribers[user_id]["tier"] = new_tier
        self.subscribers[user_id]["tier_name"] = self.tiers[new_tier]["name"]
        self.subscribers[user_id]["features"] = self.tiers[new_tier]["features"]
        self.subscribers[user_id]["rate_limits"] = self.tiers[new_tier]["rate_limits"]
        if billing_cycle:
            self.subscribers[user_id]["billing_cycle"] = billing_cycle
        self.subscribers[user_id]["active"] = True
        return {"status": "upgraded", "subscription": self.subscribers[user_id]}

    def get_subscription(self, user_id: str) -> Optional[Dict]:
        return self.subscribers.get(user_id)

    def check_feature_access(self, user_id: str, feature: str) -> bool:
        sub = self.subscribers.get(user_id)
        if not sub or not sub.get("active"):
            return self.tiers["free"]["features"].get(feature, False)
        return sub.get("features", {}).get(feature, False)

    def check_rate_limit(self, user_id: str) -> Dict:
        now = datetime.now()
        minute_key = now.strftime("%Y-%m-%d_%H:%M")
        hour_key = now.strftime("%Y-%m-%d_%H")

        if user_id not in self._usage_counts:
            self._usage_counts[user_id] = {}

        limits = self.tiers["free"]["rate_limits"]
        sub = self.subscribers.get(user_id)
        if sub and sub.get("active"):
            limits = sub.get("rate_limits", limits)

        minute_usage = self._usage_counts[user_id].get(minute_key, 0)
        hour_usage = self._usage_counts[user_id].get(hour_key, 0)

        if minute_usage >= limits["requests_per_minute"]:
            return {"allowed": False, "reason": "minute_limit", "retry_after_seconds": 60}
        if hour_usage >= limits["requests_per_hour"]:
            return {"allowed": False, "reason": "hour_limit", "retry_after_seconds": 3600}

        self._usage_counts[user_id][minute_key] = minute_usage + 1
        self._usage_counts[user_id][hour_key] = hour_usage + 1
        return {"allowed": True, "remaining_minute": limits["requests_per_minute"] - minute_usage - 1}

    def get_usage_stats(self, user_id: str) -> Dict:
        return {
            "usage_counts": self._usage_counts.get(user_id, {}),
            "subscription": self.get_subscription(user_id),
        }


premium_manager = PremiumManager()
