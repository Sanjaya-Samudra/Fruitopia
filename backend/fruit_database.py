import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class FruitDatabase:
    def __init__(self, data_dir: str = "../data/explore"):
        self.data_dir = Path(__file__).parent / data_dir
        self.fruits_data: Dict[str, Dict[str, Any]] = {}
        self.fruit_names: List[str] = []
        self.load_all_fruits()

    def load_all_fruits(self):
        """Load all fruit data from JSON files"""
        if not self.data_dir.exists():
            print(f"Warning: Fruit data directory {self.data_dir} not found")
            return

        for json_file in self.data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    fruit_data = json.load(f)
                    fruit_name = fruit_data.get('fruitName', '').lower()
                    if fruit_name:
                        self.fruits_data[fruit_name] = fruit_data
                        self.fruit_names.append(fruit_name)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

        print(f"Loaded data for {len(self.fruits_data)} fruits")

    def get_fruit_info(self, fruit_name: str) -> Optional[Dict[str, Any]]:
        """Get complete information for a specific fruit"""
        return self.fruits_data.get(fruit_name.lower())

    def search_fruits_by_disease(self, disease: str) -> List[Dict[str, Any]]:
        """Find fruits beneficial or not recommended for a specific disease"""
        results = []
        disease_lower = disease.lower()

        for fruit_name, fruit_data in self.fruits_data.items():
            medical_considerations = fruit_data.get('medicalAndDietaryConsiderations', {})

            # Check beneficial diseases
            beneficial = medical_considerations.get('beneficialForDiseases', [])
            for benefit in beneficial:
                if disease_lower in benefit.get('disease', '').lower():
                    results.append({
                        'fruit': fruit_name,
                        'type': 'beneficial',
                        'reason': benefit.get('reason', ''),
                        'recommendation': benefit.get('recommendation', ''),
                        'data': fruit_data
                    })

            # Check not recommended diseases
            not_recommended = medical_considerations.get('notRecommendedForDiseases', [])
            for contraindication in not_recommended:
                if disease_lower in contraindication.get('disease', '').lower():
                    results.append({
                        'fruit': fruit_name,
                        'type': 'not_recommended',
                        'reason': contraindication.get('reason', ''),
                        'recommendation': contraindication.get('recommendation', ''),
                        'data': fruit_data
                    })

        return results

    def get_fruit_health_benefits(self, fruit_name: str) -> List[str]:
        """Get health benefits for a specific fruit"""
        fruit_data = self.get_fruit_info(fruit_name)
        if fruit_data:
            return fruit_data.get('healthBenefits', [])
        return []

    def get_fruit_allergies(self, fruit_name: str) -> Optional[Dict[str, Any]]:
        """Get allergy information for a specific fruit"""
        fruit_data = self.get_fruit_info(fruit_name)
        if fruit_data:
            return fruit_data.get('possibleAllergies')
        return None

    def get_fruit_nutrition(self, fruit_name: str) -> Optional[Dict[str, Any]]:
        """Get nutritional facts for a specific fruit"""
        fruit_data = self.get_fruit_info(fruit_name)
        if fruit_data:
            return fruit_data.get('nutritionalFacts')
        return None

    def get_fruit_description(self, fruit_name: str) -> str:
        """Get description for a specific fruit"""
        fruit_data = self.get_fruit_info(fruit_name)
        if fruit_data:
            return fruit_data.get('description', f'{fruit_name.title()} is a nutritious fruit.')
        return f'{fruit_name.title()} is a nutritious fruit.'

    def get_similar_fruits(self, fruit_name: str) -> List[str]:
        """Get related/similar fruits"""
        fruit_data = self.get_fruit_info(fruit_name)
        if fruit_data:
            return fruit_data.get('relatedFruits', [])
        return []

    def get_fruit_warnings(self, fruit_name: str) -> List[str]:
        """Get warnings/cautions for a specific fruit"""
        fruit_data = self.get_fruit_info(fruit_name)
        if fruit_data:
            return fruit_data.get('warnings', [])
        return []

    def get_all_fruit_names(self) -> List[str]:
        """Get list of all available fruit names"""
        return self.fruit_names.copy()

# Global instance
fruit_db = FruitDatabase()

if __name__ == "__main__":
    # Test the database
    print("Available fruits:", len(fruit_db.get_all_fruit_names()))
    print("Sample fruits:", fruit_db.get_all_fruit_names()[:5])

    # Test apple data
    apple_info = fruit_db.get_fruit_info("apple")
    if apple_info:
        print(f"\nApple description: {apple_info.get('description', '')[:100]}...")
        print(f"Apple health benefits: {fruit_db.get_fruit_health_benefits('apple')[:2]}")

    # Test disease search
    diabetes_fruits = fruit_db.search_fruits_by_disease("diabetes")
    print(f"\nFruits for diabetes: {len(diabetes_fruits)}")
    for fruit in diabetes_fruits[:3]:
        print(f"- {fruit['fruit']}: {fruit['type']} - {fruit['reason'][:50]}...")