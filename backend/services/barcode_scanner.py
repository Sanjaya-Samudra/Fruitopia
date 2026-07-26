"""Barcode scanner service for fruit lookup via UPC/EAN codes."""

from typing import Dict, List, Optional
import json
from pathlib import Path

FILE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = FILE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
EXPLORE_DIR = DATA_DIR / "explore"

# Simulated barcode database for common fruits
# In production, use Open Food Facts / USDA branded food database APIs
FRUIT_BARCODES = {
    "040100000101": {"fruit": "apple", "variety": "Gala", "brand": "Generic", "country": "USA"},
    "040100000102": {"fruit": "banana", "variety": "Cavendish", "brand": "Generic", "country": "Ecuador"},
    "040100000103": {"fruit": "orange", "variety": "Navel", "brand": "Generic", "country": "USA"},
    "040100000104": {"fruit": "grape", "variety": "Red Seedless", "brand": "Generic", "country": "USA"},
    "040100000105": {"fruit": "strawberry", "variety": "Garden", "brand": "Generic", "country": "USA"},
    "040100000106": {"fruit": "blueberry", "variety": "Highbush", "brand": "Generic", "country": "Canada"},
    "040100000107": {"fruit": "avocado", "variety": "Hass", "brand": "Generic", "country": "Mexico"},
    "040100000108": {"fruit": "lemon", "variety": "Eureka", "brand": "Generic", "country": "USA"},
    "040100000109": {"fruit": "lime", "variety": "Persian", "brand": "Generic", "country": "Mexico"},
    "040100000110": {"fruit": "watermelon", "variety": "Seedless", "brand": "Generic", "country": "USA"},
    "040100000111": {"fruit": "pineapple", "variety": "Smooth Cayenne", "brand": "Generic", "country": "Costa Rica"},
    "040100000112": {"fruit": "mango", "variety": "Kent", "brand": "Generic", "country": "Peru"},
    "040100000113": {"fruit": "kiwi", "variety": "Hayward", "brand": "Generic", "country": "New Zealand"},
    "040100000114": {"fruit": "papaya", "variety": "Maradol", "brand": "Generic", "country": "Mexico"},
    "040100000115": {"fruit": "grapefruit", "variety": "Ruby Red", "brand": "Generic", "country": "USA"},
    "040100000116": {"fruit": "pear", "variety": "Bartlett", "brand": "Generic", "country": "USA"},
    "040100000117": {"fruit": "peach", "variety": "Yellow", "brand": "Generic", "country": "USA"},
    "040100000118": {"fruit": "plum", "variety": "Black", "brand": "Generic", "country": "USA"},
    "040100000119": {"fruit": "cherry", "variety": "Bing", "brand": "Generic", "country": "USA"},
    "040100000120": {"fruit": "pomegranate", "variety": "Wonderful", "brand": "Generic", "country": "USA"},
    "040100000121": {"fruit": "coconut", "variety": "Young", "brand": "Generic", "country": "Thailand"},
    "040100000122": {"fruit": "dragonfruit", "variety": "White Flesh", "brand": "Generic", "country": "Vietnam"},
    "040100000123": {"fruit": "passionfruit", "variety": "Purple", "brand": "Generic", "country": "Brazil"},
    "040100000124": {"fruit": "guava", "variety": "Pink", "brand": "Generic", "country": "India"},
    "040100000125": {"fruit": "lychee", "variety": "Sweetheart", "brand": "Generic", "country": "China"},
    "040100000126": {"fruit": "raspberry", "variety": "Red", "brand": "Generic", "country": "USA"},
    "040100000127": {"fruit": "blackberry", "variety": "Marion", "brand": "Generic", "country": "USA"},
    "040100000128": {"fruit": "cranberry", "variety": "American", "brand": "Generic", "country": "USA"},
    "040100000129": {"fruit": "fig", "variety": "Black Mission", "brand": "Generic", "country": "USA"},
    "040100000130": {"fruit": "date", "variety": "Medjool", "brand": "Generic", "country": "Israel"},

    # International barcode prefix examples (simulated)
    "8901234567890": {"fruit": "mango", "variety": "Alphonso", "brand": "Ratnagiri Farms", "country": "India"},
    "6901234567890": {"fruit": "lychee", "variety": "Nuomici", "brand": "Guangdong Harvest", "country": "China"},
    "8801234567890": {"fruit": "persimmon", "variety": "Fuyu", "brand": "Sweet Persimmon Co.", "country": "South Korea"},
    "6001234567890": {"fruit": "soursop", "variety": "Brazilian", "brand": "Tropical Delight", "country": "Brazil"},
    "9401234567890": {"fruit": "kiwi", "variety": "Gold", "brand": "Zespri", "country": "New Zealand"},
    "8401234567890": {"fruit": "avocado", "variety": "Fuerte", "brand": "Michoacan Groves", "country": "Mexico"},
    "7401234567890": {"fruit": "banana", "variety": "Red", "brand": "Ecuadorian Exports", "country": "Ecuador"},
    "5401234567890": {"fruit": "coconut", "variety": "Mature", "brand": "Philippine Farms", "country": "Philippines"},
}


class BarcodeScanner:
    """Service for barcode-based fruit identification and lookup."""

    def __init__(self):
        self.barcode_db = FRUIT_BARCODES
        self.scan_history = []

    def lookup_barcode(self, barcode: str) -> Dict:
        result = self.barcode_db.get(barcode.strip())
        if result:
            entry = {
                "found": True,
                "barcode": barcode,
                "fruit": result["fruit"],
                "variety": result.get("variety", "Unknown"),
                "brand": result.get("brand", "Generic"),
                "country_of_origin": result.get("country", "Unknown"),
            }
        else:
            prefix = self._guess_from_prefix(barcode)
            entry = {
                "found": False,
                "barcode": barcode,
                "fruit": prefix,
                "message": "Exact match not found. Check USDA branded food database.",
            }

        self.scan_history.append({
            "barcode": barcode,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "result": entry,
        })
        return entry

    def _guess_from_prefix(self, barcode: str) -> Optional[str]:
        prefix_map = {
            "04": "apple", "401": "banana", "404": "orange",
            "94": "kiwi", "84": "avocado", "74": "banana",
            "69": "lychee", "89": "mango", "88": "persimmon",
            "60": "tropical", "54": "coconut",
        }
        for prefix, guess in prefix_map.items():
            if barcode.startswith(prefix):
                return guess
        return None

    def get_scan_history(self, limit: int = 20) -> List[Dict]:
        return self.scan_history[-limit:]

    def validate_barcode(self, barcode: str) -> Dict:
        if not barcode or not barcode.isdigit():
            return {"valid": False, "message": "Barcode must contain only digits"}
        if len(barcode) not in (8, 12, 13, 14):
            return {"valid": False, "message": "Invalid barcode length (must be 8, 12, 13, or 14 digits)"}
        return {"valid": True, "format": f"UPC-{len(barcode)}"}

    def search_by_country(self, country: str) -> List[Dict]:
        results = []
        for barcode, info in self.barcode_db.items():
            if country.lower() in info.get("country", "").lower():
                results.append({
                    "barcode": barcode,
                    **info,
                })
        return results


barcode_scanner = BarcodeScanner()
