"""Fruit culture encyclopedia - cultivation, trade, sustainability, and global fruit knowledge."""

from typing import Dict, List, Optional
from datetime import datetime

# Comprehensive fruit culture data
FRUIT_CULTURE = {
    "apple": {
        "cultivation": {
            "origin": "Central Asia (Kazakhstan, Kyrgyzstan)",
            "primary_regions": ["China", "USA", "Poland", "Turkey", "Italy"],
            "growing_season": "Spring bloom, Fall harvest",
            "climate": "Temperate, requires 500-1000 chill hours",
            "soil": "Well-drained loam, pH 6.0-7.0",
            "water_needs": "Moderate, 50-80 cm annual rainfall",
            "harvest_method": "Hand-picked or mechanical shaker",
            "yield_per_hectare": "20-40 tonnes",
            "days_to_maturity": "100-200 days post-bloom",
        },
        "trade": {
            "global_production_tonnes": 86000000,
            "top_exporters": ["China", "USA", "Poland", "Italy", "Chile"],
            "top_importers": ["Germany", "UK", "Russia", "India", "USA"],
            "average_price_per_kg": "$1.20",
            "seasonal_peak": "September-November",
            "trade_value_billion": "$12.5",
        },
        "sustainability": {
            "carbon_footprint_kgCO2perkg": 0.43,
            "water_footprint_Lperkg": 822,
            "pesticide_load": "Medium (top 10 in EWG Dirty Dozen)",
            "organic_share": "12% of total production",
            "post_harvest_loss": "15-20% in supply chain",
            "storage_life": "3-12 months (controlled atmosphere)",
        },
        "varieties": ["Gala", "Fuji", "Granny Smith", "Honeycrisp", "Red Delicious", "Pink Lady", "Braeburn", "McIntosh", "Golden Delicious", "Cosmic Crisp"],
        "fun_facts": [
            "There are over 7,500 apple varieties grown worldwide",
            "Apple trees can live for over 100 years",
            "China produces nearly half of the world's apples",
            "Apples float because they are 25% air by volume",
            "The science of apple growing is called pomology",
        ],
    },
    "banana": {
        "cultivation": {
            "origin": "Southeast Asia (Papua New Guinea, Indonesia)",
            "primary_regions": ["India", "China", "Philippines", "Ecuador", "Brazil"],
            "growing_season": "Year-round in tropics",
            "climate": "Tropical, 20-35°C, high humidity",
            "soil": "Deep, well-drained alluvial or volcanic soil, pH 5.5-7.0",
            "water_needs": "High, 100-200 cm annual rainfall or irrigation",
            "harvest_method": "Hand-cut bunches, 9-12 months after planting",
            "yield_per_hectare": "30-60 tonnes",
            "days_to_maturity": "300-365 days from planting",
        },
        "trade": {
            "global_production_tonnes": 125000000,
            "top_exporters": ["Ecuador", "Philippines", "Costa Rica", "Colombia", "Guatemala"],
            "top_importers": ["USA", "EU", "China", "Russia", "Japan"],
            "average_price_per_kg": "$0.90",
            "seasonal_peak": "Year-round",
            "trade_value_billion": "$13.2",
        },
        "sustainability": {
            "carbon_footprint_kgCO2perkg": 0.48,
            "water_footprint_Lperkg": 790,
            "pesticide_load": "High (monoculture disease pressure)",
            "organic_share": "8% of global trade",
            "post_harvest_loss": "25-40% in supply chain",
            "storage_life": "2-7 days ripe, 14-21 days green",
        },
        "varieties": ["Cavendish", "Red", "Lady Finger", "Plantain", "Blue Java", "Burro", "Manzano", "Grand Nain", "Williams hybrid", "Gros Michel"],
        "fun_facts": [
            "Bananas are technically berries, while strawberries are not",
            "The Cavendish banana accounts for 47% of global production",
            "Bananas are the most traded fruit by volume in the world",
            "A cluster of bananas is called a 'hand', each banana is a 'finger'",
            "The word 'banana' comes from the Arabic word 'banan' meaning finger",
        ],
    },
    "orange": {
        "cultivation": {
            "origin": "Southeast Asia (China, India)",
            "primary_regions": ["Brazil", "USA", "India", "China", "Mexico"],
            "growing_season": "Winter harvest (Northern Hemisphere: Nov-Mar)",
            "climate": "Subtropical, 15-30°C, frost-sensitive",
            "soil": "Well-drained sandy loam, pH 5.5-6.5",
            "water_needs": "Moderate-high, 60-120 cm annual rainfall",
            "harvest_method": "Hand-picked or mechanical",
            "yield_per_hectare": "25-40 tonnes",
            "days_to_maturity": "240-360 days post-bloom",
        },
        "trade": {
            "global_production_tonnes": 75000000,
            "top_exporters": ["Spain", "South Africa", "USA", "Egypt", "Turkey"],
            "top_importers": ["EU", "China", "USA", "Canada", "Japan"],
            "average_price_per_kg": "$1.10",
            "seasonal_peak": "December-March",
            "trade_value_billion": "$8.9",
            "note": "60% of oranges are processed into juice",
        },
        "sustainability": {
            "carbon_footprint_kgCO2perkg": 0.39,
            "water_footprint_Lperkg": 560,
            "pesticide_load": "Medium",
            "organic_share": "7%",
            "post_harvest_loss": "10-15%",
            "storage_life": "3-8 weeks",
        },
        "varieties": ["Navel", "Valencia", "Blood Orange", "Cara Cara", "Seville", "Moro", "Trovita", "Hamlin", "Pineapple Orange", "Jaffa"],
        "fun_facts": [
            "Brazil produces one-third of the world's oranges",
            "The orange is actually a hybrid of pomelo and mandarin",
            "NASA studies orange nutrition for long-duration space missions",
            "Florida's orange industry was devastated by citrus greening disease",
            "Spanish explorers brought oranges to the Americas in the 1500s",
        ],
    },
    "mango": {
        "cultivation": {
            "origin": "South Asia (India, Myanmar)",
            "primary_regions": ["India", "China", "Thailand", "Indonesia", "Mexico"],
            "growing_season": "Summer harvest (Apr-Aug in tropics)",
            "climate": "Tropical, 25-35°C, dry season for flowering",
            "soil": "Well-drained loam to laterite, pH 5.5-7.5",
            "water_needs": "Moderate, dry spell needed for flowering",
            "harvest_method": "Hand-picked with poles",
            "yield_per_hectare": "10-25 tonnes",
            "days_to_maturity": "100-150 days from flowering",
        },
        "trade": {
            "global_production_tonnes": 56000000,
            "top_exporters": ["India", "Thailand", "Mexico", "Peru", "Brazil"],
            "top_importers": ["USA", "China", "Netherlands", "UAE", "UK"],
            "average_price_per_kg": "$1.80",
            "seasonal_peak": "May-August",
            "trade_value_billion": "$6.8",
        },
        "sustainability": {
            "carbon_footprint_kgCO2perkg": 0.36,
            "water_footprint_Lperkg": 625,
            "pesticide_load": "Medium",
            "organic_share": "5%",
            "post_harvest_loss": "20-30%",
            "storage_life": "7-21 days",
        },
        "varieties": ["Alphonso", "Kent", "Tommy Atkins", "Ataulfo", "Keitt", "Haden", "Nam Dok Mai", "Chaunsa", "Langra", "Dasheri"],
        "fun_facts": [
            "India produces over 45% of the world's mangoes",
            "The mango is the national fruit of India, Pakistan, and the Philippines",
            "There are over 1,000 mango varieties worldwide",
            "Mango trees can live and produce fruit for over 300 years",
            "Alphonso mangoes are considered the finest variety globally",
        ],
    },
}

DEFAULT_FRUIT = {
    "cultivation": {
        "origin": "Global cultivation",
        "primary_regions": ["Tropical", "Subtropical", "Temperate regions"],
        "growing_season": "Varies by region and variety",
        "climate": "Varies by species",
        "soil": "Well-drained soil, pH 6.0-7.0",
        "water_needs": "Moderate",
        "harvest_method": "Varies",
        "yield_per_hectare": "Varies",
        "days_to_maturity": "Varies",
    },
    "trade": {
        "global_production_tonnes": 0,
        "top_exporters": [],
        "top_importers": [],
        "average_price_per_kg": "$?",
        "seasonal_peak": "Varies",
        "trade_value_billion": "$?",
    },
    "sustainability": {
        "carbon_footprint_kgCO2perkg": 0,
        "water_footprint_Lperkg": 0,
        "pesticide_load": "Unknown",
        "organic_share": "Unknown",
        "post_harvest_loss": "Unknown",
        "storage_life": "Varies",
    },
    "varieties": [],
    "fun_facts": ["Fruits are nature's original packaged food!"],
}

# Global fruit production stats (FAO 2023-24 approximations)
GLOBAL_FRUIT_STATS = {
    "total_global_fruit_production_tonnes": 900_000_000,
    "total_area_harvested_hectares": 65_000_000,
    "number_of_commercially_grown_fruit_species": 150,
    "estimated_wild_edible_fruit_species": 3000,
    "percentage_of_fruit_lost_post_harvest": "35-45% in developing countries",
    "organic_fruit_market_size_billion": 45,
    "fruit_export_value_billion_annually": 180,
    "most_traded_fruit": "Banana (by volume), Apple (by value)",
    "fastest_growing_fruit_category": "Berries (especially blueberries & goji)",
    "countries_with_most_fruit_varieties": ["India", "China", "Indonesia", "Brazil", "Mexico"],
}

# Seasonal calendars for major growing regions
SEASONAL_CALENDARS = {
    "northern_hemisphere": {
        "spring": ["strawberry", "rhubarb", "cherry", "apricot", "mango"],
        "summer": ["watermelon", "blueberry", "peach", "plum", "nectarine", "raspberry", "fig", "grape", "lychee"],
        "fall": ["apple", "pear", "grape", "pomegranate", "cranberry", "persimmon", "quince", "kiwi"],
        "winter": ["orange", "grapefruit", "clementine", "pomelo", "date", "coconut", "papaya", "dragonfruit"],
    },
    "southern_hemisphere": {
        "spring": ["apple", "pear", "grape", "kiwi", "avocado"],
        "summer": ["orange", "grapefruit", "lemon", "strawberry", "cherry"],
        "fall": ["mango", "banana", "papaya", "pineapple", "passionfruit"],
        "winter": ["watermelon", "peach", "plum", "grape", "fig"],
    },
    "tropical": {
        "year_round": ["banana", "papaya", "pineapple", "coconut", "guava", "dragonfruit"],
        "wet_season": ["mango", "rambutan", "durian", "mangosteen", "jackfruit", "soursop"],
        "dry_season": ["passionfruit", "lychee", "longan", "starfruit", "tamarind"],
    },
}


class FruitCulture:
    """Encyclopedia for global fruit cultivation, trade, and sustainability data."""

    def __init__(self):
        self.culture_db = FRUIT_CULTURE
        self.stats = GLOBAL_FRUIT_STATS
        self.seasonal = SEASONAL_CALENDARS

    def get_cultivation_info(self, fruit_name: str) -> dict:
        fruit = fruit_name.lower().strip()
        entry = self.culture_db.get(fruit)
        return entry["cultivation"] if entry else DEFAULT_FRUIT["cultivation"]

    def get_trade_info(self, fruit_name: str) -> dict:
        fruit = fruit_name.lower().strip()
        entry = self.culture_db.get(fruit)
        return entry["trade"] if entry else DEFAULT_FRUIT["trade"]

    def get_sustainability_info(self, fruit_name: str) -> dict:
        fruit = fruit_name.lower().strip()
        entry = self.culture_db.get(fruit)
        return entry["sustainability"] if entry else DEFAULT_FRUIT["sustainability"]

    def get_varieties(self, fruit_name: str) -> List[str]:
        fruit = fruit_name.lower().strip()
        entry = self.culture_db.get(fruit)
        return entry.get("varieties", DEFAULT_FRUIT["varieties"]) if entry else DEFAULT_FRUIT["varieties"]

    def get_fun_facts(self, fruit_name: str) -> List[str]:
        fruit = fruit_name.lower().strip()
        entry = self.culture_db.get(fruit)
        return entry.get("fun_facts", DEFAULT_FRUIT["fun_facts"]) if entry else DEFAULT_FRUIT["fun_facts"]

    def get_all_fruit_cultures(self) -> Dict[str, dict]:
        return {
            name: {
                "origin": data["cultivation"]["origin"],
                "primary_regions": data["cultivation"]["primary_regions"],
                "global_production_tonnes": data["trade"]["global_production_tonnes"],
                "variety_count": len(data.get("varieties", [])),
                "fun_fact_count": len(data.get("fun_facts", [])),
            }
            for name, data in self.culture_db.items()
        }

    def get_global_stats(self) -> dict:
        return self.stats

    def get_seasonal_fruits(self, hemisphere: str = "northern_hemisphere", season: str = None) -> dict:
        cal = self.seasonal.get(hemisphere, self.seasonal["northern_hemisphere"])
        if season:
            return {"hemisphere": hemisphere, "season": season, "fruits": cal.get(season, [])}
        return {"hemisphere": hemisphere, "calendars": cal}

    def get_tropical_calendar(self) -> dict:
        return self.seasonal.get("tropical", {})

    def compare_fruits(self, fruit_a: str, fruit_b: str) -> dict:
        a = self.culture_db.get(fruit_a.lower(), DEFAULT_FRUIT)
        b = self.culture_db.get(fruit_b.lower(), DEFAULT_FRUIT)
        return {
            "fruit_a": fruit_a,
            "fruit_b": fruit_b,
            "comparison": {
                "production_a_tonnes": a.get("trade", {}).get("global_production_tonnes", 0),
                "production_b_tonnes": b.get("trade", {}).get("global_production_tonnes", 0),
                "origin_a": a.get("cultivation", {}).get("origin", "Unknown"),
                "origin_b": b.get("cultivation", {}).get("origin", "Unknown"),
                "carbon_a_kgCO2": a.get("sustainability", {}).get("carbon_footprint_kgCO2perkg", 0),
                "carbon_b_kgCO2": b.get("sustainability", {}).get("carbon_footprint_kgCO2perkg", 0),
                "varieties_a": len(a.get("varieties", [])),
                "varieties_b": len(b.get("varieties", [])),
            }
        }

    def search_culture(self, query: str) -> dict:
        q = query.lower()
        results = {"fruits": [], "regions": [], "varieties": []}
        for fruit_name, data in self.culture_db.items():
            if q in fruit_name:
                results["fruits"].append({
                    "name": fruit_name,
                    "origin": data["cultivation"]["origin"],
                })
            for region in data["cultivation"]["primary_regions"]:
                if q in region.lower():
                    results["regions"].append({
                        "fruit": fruit_name,
                        "region": region,
                    })
            for variety in data.get("varieties", []):
                if q in variety.lower():
                    results["varieties"].append({
                        "fruit": fruit_name,
                        "variety": variety,
                    })
        return results


fruit_culture = FruitCulture()
