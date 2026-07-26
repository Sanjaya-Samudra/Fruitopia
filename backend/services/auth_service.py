"""User authentication and profile management service."""

import hashlib
import json
import os
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

FILE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = FILE_DIR.parent / "data"
USERS_FILE = DATA_DIR / "users.json"

os.makedirs(DATA_DIR, exist_ok=True)


def _hash_password(password: str, salt: str = None) -> tuple:
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, pwd_hash


def _verify_password(password: str, salt: str, stored_hash: str) -> bool:
    _, check = _hash_password(password, salt)
    return check == stored_hash


class UserStore:
    """Simple file-based user store. Replace with PostgreSQL in production."""

    def __init__(self):
        self.users: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if USERS_FILE.exists():
            try:
                with open(USERS_FILE, "r") as f:
                    self.users = json.load(f)
            except Exception:
                self.users = {}

    def _save(self):
        with open(USERS_FILE, "w") as f:
            json.dump(self.users, f, indent=2, default=str)

    def create_user(self, email: str, password: str, name: str) -> dict:
        if email in self.users:
            raise ValueError("Email already registered")
        salt, pwd_hash = _hash_password(password)
        user = {
            "email": email,
            "name": name,
            "password_hash": pwd_hash,
            "password_salt": salt,
            "created_at": datetime.now().isoformat(),
            "profile": {
                "age": None,
                "gender": None,
                "weight_kg": None,
                "height_cm": None,
                "activity_level": "moderate",
                "health_conditions": [],
                "allergies": [],
                "dietary_preferences": [],
                "goals": [],
                "disliked_fruits": [],
            },
            "history": {
                "recommendations_viewed": [],
                "feedback": [],
                "searches": [],
                "chat_sessions": [],
            },
            "preferences": {
                "theme": "light",
                "notifications": True,
                "meal_plan_servings": 2,
            },
        }
        self.users[email] = user
        self._save()
        return self._sanitize(user)

    def authenticate(self, email: str, password: str) -> Optional[dict]:
        user = self.users.get(email)
        if not user:
            return None
        if _verify_password(password, user["password_salt"], user["password_hash"]):
            return self._sanitize(user)
        return None

    def get_user(self, email: str) -> Optional[dict]:
        user = self.users.get(email)
        return self._sanitize(user) if user else None

    def update_profile(self, email: str, updates: dict) -> Optional[dict]:
        user = self.users.get(email)
        if not user:
            return None
        profile = user.get("profile", {})
        for key, value in updates.items():
            if key in profile:
                profile[key] = value
        user["profile"] = profile
        self.users[email] = user
        self._save()
        return self._sanitize(user)

    def add_history(self, email: str, category: str, entry: Any):
        user = self.users.get(email)
        if not user:
            return
        if category not in user.get("history", {}):
            user["history"] = user.get("history", {})
            user["history"][category] = []
        user["history"][category].append({
            "timestamp": datetime.now().isoformat(),
            "data": entry if not isinstance(entry, dict) else entry,
        })
        if len(user["history"][category]) > 100:
            user["history"][category] = user["history"][category][-100:]
        self.users[email] = user
        self._save()

    def _sanitize(self, user: dict) -> dict:
        safe = dict(user)
        safe.pop("password_hash", None)
        safe.pop("password_salt", None)
        return safe


user_store = UserStore()


class SessionManager:
    """Simple session token management."""

    def __init__(self):
        self.tokens: Dict[str, dict] = {}

    def create_session(self, email: str) -> str:
        token = secrets.token_hex(32)
        self.tokens[token] = {
            "email": email,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
        }
        return token

    def validate_session(self, token: str) -> Optional[str]:
        session = self.tokens.get(token)
        if not session:
            return None
        expires = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires:
            self.tokens.pop(token, None)
            return None
        return session["email"]

    def revoke_session(self, token: str):
        self.tokens.pop(token, None)

    def get_user_email(self, token: str) -> Optional[str]:
        return self.validate_session(token)


session_manager = SessionManager()
