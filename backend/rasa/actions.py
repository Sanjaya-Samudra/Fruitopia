from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker  # type: ignore
from rasa_sdk.executor import CollectingDispatcher  # type: ignore
from rasa_sdk.events import SlotSet  # type: ignore
import json
import os
import sys
from pathlib import Path

# Add backend directory to path to import fruit_database
sys.path.append(str(Path(__file__).parent.parent))
from fruit_database import fruit_db

class ActionRecommendFruits(Action):

    def name(self) -> Text:
        return "action_recommend_fruits"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        disease = tracker.get_slot("disease")
        if not disease:
            dispatcher.utter_message(text="I need to know your health condition to recommend fruits. Please tell me what condition you have.")
            return []

        # Use the rich fruit database to find recommendations
        disease_results = fruit_db.search_fruits_by_disease(disease)

        beneficial_fruits = [r for r in disease_results if r['type'] == 'beneficial']
        not_recommended = [r for r in disease_results if r['type'] == 'not_recommended']

        response_text = f"For **{disease.title()}**, here are some fruit recommendations:\n\n"

        if beneficial_fruits:
            response_text += "**Recommended fruits:**\n"
            for fruit in beneficial_fruits[:4]:  # Limit to 4 recommendations
                fruit_name = fruit['fruit'].title()
                reason = fruit['reason'][:100] + "..." if len(fruit['reason']) > 100 else fruit['reason']
                response_text += f"🍎 **{fruit_name}**: {reason}\n"
        else:
            # Fallback to general healthy fruits
            response_text += "While I don't have specific recommendations for this condition, here are some generally healthy fruits:\n"
            general_fruits = ['blueberries', 'apples', 'oranges', 'bananas']
            for fruit_name in general_fruits[:3]:
                benefits = fruit_db.get_fruit_health_benefits(fruit_name)
                if benefits:
                    response_text += f"🍎 **{fruit_name.title()}**: {benefits[0]}\n"

        if not_recommended:
            response_text += f"\n⚠️ **Fruits to avoid or limit** for {disease.title()}:\n"
            for fruit in not_recommended[:2]:
                fruit_name = fruit['fruit'].title()
                reason = fruit['reason'][:80] + "..." if len(fruit['reason']) > 80 else fruit['reason']
                response_text += f"❌ **{fruit_name}**: {reason}\n"

        dispatcher.utter_message(text=response_text)

        # Update conversation memory
        memory = tracker.get_slot("conversation_memory") or []
        memory.append(f"Recommended fruits for {disease}")
        return [SlotSet("conversation_memory", memory)]

class ActionGetFruitInfo(Action):

    def name(self) -> Text:
        return "action_get_fruit_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        fruit = tracker.get_slot("fruit")
        if not fruit:
            dispatcher.utter_message(text="Which fruit would you like information about?")
            return []

        fruit_info = fruit_db.get_fruit_info(fruit)
        if not fruit_info:
            dispatcher.utter_message(text=f"I'm sorry, I don't have detailed information about {fruit}. Here are some fruits I know about: {', '.join(fruit_db.get_all_fruit_names()[:10])}")
            return []

        # Build comprehensive response
        response_parts = []

        # Basic info
        fruit_name = fruit_info.get('fruitName', fruit.title())
        scientific_name = fruit_info.get('scientificName', '')
        description = fruit_info.get('description', '')[:200] + "..." if len(fruit_info.get('description', '')) > 200 else fruit_info.get('description', '')

        response_parts.append(f"🍎 **{fruit_name}**")
        if scientific_name:
            response_parts.append(f"_{scientific_name}_")
        response_parts.append(f"{description}")

        # Nutritional highlights
        nutrition = fruit_db.get_fruit_nutrition(fruit)
        if nutrition:
            calories = nutrition.get('calories_kcal', 'N/A')
            fiber = nutrition.get('macronutrients', {}).get('fiber_g', 'N/A')
            vitamin_c = nutrition.get('vitamins', {}).get('vitaminC_mg', 'N/A')
            response_parts.append(f"\n📊 **Nutrition** (per {nutrition.get('servingSize_g', 100)}g): {calories} kcal, {fiber}g fiber, {vitamin_c}mg vitamin C")

        # Health benefits
        benefits = fruit_db.get_fruit_health_benefits(fruit)
        if benefits:
            response_parts.append(f"\n💚 **Health Benefits**:")
            for benefit in benefits[:3]:  # Show top 3 benefits
                response_parts.append(f"• {benefit}")

        # Allergies warning
        allergies = fruit_db.get_fruit_allergies(fruit)
        if allergies and allergies.get('allergens'):
            severity = allergies.get('allergenSeverity', 'unknown')
            response_parts.append(f"\n⚠️ **Allergy Note**: May cause {severity} reactions in sensitive individuals")

        # Warnings
        warnings = fruit_db.get_fruit_warnings(fruit)
        if warnings:
            response_parts.append(f"\n🚨 **Important**: {warnings[0]}")

        # Related fruits
        related = fruit_db.get_similar_fruits(fruit)
        if related:
            response_parts.append(f"\n🍓 **Similar fruits**: {', '.join(related[:3])}")

        full_response = "\n".join(response_parts)
        dispatcher.utter_message(text=full_response)

        # Update memory
        memory = tracker.get_slot("conversation_memory") or []
        memory.append(f"Provided info about {fruit}")
        return [SlotSet("conversation_memory", memory)]

class ActionGetFruitComparison(Action):

    def name(self) -> Text:
        return "action_get_fruit_comparison"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # This could be enhanced to compare two fruits
        dispatcher.utter_message(text="I'd be happy to help you compare fruits! Could you tell me which two fruits you'd like to compare?")
        return []

class ActionGetFruitRecipes(Action):

    def name(self) -> Text:
        return "action_get_fruit_recipes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        fruit = tracker.get_slot("fruit")
        if not fruit:
            dispatcher.utter_message(text="Which fruit would you like recipes for?")
            return []

        fruit_info = fruit_db.get_fruit_info(fruit)
        if fruit_info:
            recipes = fruit_info.get('howToEat', {}).get('recipes', [])
            if recipes:
                response = f"Here are some delicious ways to enjoy {fruit.title()}:\n\n"
                for recipe in recipes[:5]:
                    response += f"🍽️ {recipe.title()}\n"
                dispatcher.utter_message(text=response)
            else:
                dispatcher.utter_message(text=f"{fruit.title()} is delicious fresh! You can also try smoothies, salads, or baking with it.")
        else:
            dispatcher.utter_message(text=f"I don't have specific recipes for {fruit}, but most fruits are great in smoothies, salads, or desserts!")

        return []