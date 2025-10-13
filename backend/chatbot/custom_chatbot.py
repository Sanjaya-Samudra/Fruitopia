#!/usr/bin/env python3
"""
Custom Transformer-based Chatbot for Fruitopia
Uses modern NLP libraries instead of Rasa for better Python 3.12 compatibility
"""

import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re

class FruitopiaChatbot:
    """Custom transformer-based chatbot for fruit recommendations and information"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the chatbot with a sentence transformer model"""
        self.model = SentenceTransformer(model_name)
        self.intents = {}
        self.responses = {}
        self.intent_embeddings = None
        self.fruit_database = None

        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)

        self.stop_words = set(stopwords.words('english'))

    def load_fruit_database(self, data_path: str = None):
        """Load the comprehensive fruit database"""
        if data_path is None:
            # Try to find the data directory relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            data_path = os.path.join(project_root, 'data', 'explore')

        if not os.path.exists(data_path):
            print(f"Warning: Fruit database path {data_path} not found")
            return

        self.fruit_database = {}
        fruit_files = [f for f in os.listdir(data_path) if f.endswith('.json')]

        for file in fruit_files:
            fruit_name = file.replace('.json', '')
            try:
                with open(os.path.join(data_path, file), 'r', encoding='utf-8') as f:
                    self.fruit_database[fruit_name] = json.load(f)
            except Exception as e:
                print(f"Error loading {file}: {e}")

        print(f"Loaded {len(self.fruit_database)} fruits from database")

    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better matching"""
        # Convert to lowercase
        text = text.lower()

        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)

        # Tokenize and remove stop words
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token not in self.stop_words]

        return ' '.join(tokens)

    def load_training_data(self, data_path: str = None):
        """Load training data with intents and responses"""
        if data_path is None:
            # Default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(current_dir, 'data', 'training_data.json')
        if not os.path.exists(data_path):
            self._create_default_training_data(data_path)

        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.intents = data.get('intents', {})
            self.responses = data.get('responses', {})

            # Create embeddings for all intent examples
            all_examples = []
            self.intent_map = []

            for intent, examples in self.intents.items():
                for example in examples:
                    all_examples.append(self.preprocess_text(example))
                    self.intent_map.append(intent)

            if all_examples:
                self.intent_embeddings = self.model.encode(all_examples)
                print(f"Loaded {len(self.intents)} intents with {len(all_examples)} training examples")

        except Exception as e:
            print(f"Error loading training data: {e}")
            self._create_default_training_data(data_path)

    def _create_default_training_data(self, data_path: str):
        """Create comprehensive training data with many more intents and examples"""
        print("Creating comprehensive training data...")

        self.intents = {
            "greet": [
                "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
                "howdy", "greetings", "what's up", "hey there", "hi there", "hello there",
                "good day", "nice to meet you", "pleased to meet you"
            ],
            "goodbye": [
                "bye", "goodbye", "see you later", "farewell", "take care", "bye bye",
                "see you", "good night", "have a good day", "see you soon", "talk to you later",
                "catch you later", "until next time"
            ],
            "recommend_fruits": [
                "what fruits should I eat", "recommend fruits for me", "suggest fruits",
                "which fruits are good for", "fruits for health", "fruit recommendations",
                "I have a condition", "I'm suffering from", "I need fruits for",
                "what should I eat", "healthy fruits", "best fruits for"
            ],
            "fruit_info": [
                "tell me about", "what is", "information about", "details on",
                "facts about", "nutrition of", "benefits of", "calories in",
                "how many calories", "nutritional value", "what's in", "explain"
            ],
            "disease_specific": [
                "diabetes", "diabetic", "blood sugar", "high blood pressure", "hypertension",
                "heart disease", "cholesterol", "weight loss", "obesity", "cancer",
                "immune system", "digestion", "constipation", "inflammation", "arthritis",
                "bone health", "anemia", "thyroid", "kidney", "liver", "asthma", "depression",
                "memory", "brain health", "skin health", "hair health", "eyesight", "vision"
            ],
            "quantity_amount": [
                "how much", "how many", "quantity", "amount", "serving size",
                "portion", "daily amount", "recommended daily", "per day"
            ],
            "seasonal_availability": [
                "when is in season", "available now", "fresh now", "current season",
                "best time for", "when to buy", "seasonal fruits"
            ],
            "recipes_cooking": [
                "how to cook", "recipes with", "how to prepare", "cooking tips",
                "fruit salad", "smoothie recipe", "juice recipe", "fruit dessert"
            ],
            "allergy_warnings": [
                "allergic to", "allergy", "can't eat", "avoid", "intolerant to",
                "sensitive to", "reaction to", "not good for me"
            ],
            "shopping_cart": [
                "add to cart", "buy", "purchase", "order", "shopping list",
                "I want to buy", "where to buy", "price of"
            ],
            "comparison": [
                "vs", "versus", "better than", "which is better", "compare",
                "difference between", "which has more", "which is healthier"
            ],
            "general_health": [
                "healthy eating", "nutrition tips", "diet advice", "weight management",
                "energy boost", "immunity boost", "detox", "anti-aging", "beauty"
            ],
            "organic_natural": [
                "organic", "natural", "pesticide free", "GMO free", "conventional vs organic",
                "farming methods", "sustainable", "environmentally friendly"
            ],
            "storage_preservation": [
                "how to store", "storage tips", "how long does it last", "keep fresh",
                "ripening", "refrigerator", "room temperature", "freezer"
            ],
            "origin_geography": [
                "where does it come from", "origin", "country of origin", "imported",
                "local", "grown in", "cultivated in", "native to"
            ],
            "fun_facts": [
                "interesting facts", "fun facts", "did you know", "trivia",
                "history of", "origin story", "unique facts"
            ],
            "meal_planning": [
                "meal ideas", "breakfast ideas", "snack ideas", "lunch ideas",
                "dinner ideas", "meal prep", "weekly meal plan"
            ]
        }

        self.responses = {
            "greet": [
                "Hello! I'm your fruit expert from Fruitopia. I can help you discover amazing fruits for your health and wellness. What would you like to know?",
                "Hi there! Welcome to Fruitopia. I'm here to help you find the perfect fruits for your needs. How can I assist you today?",
                "Greetings! I'm your friendly fruit nutritionist. I know everything about fruits and their health benefits. What can I help you with?",
                "Hey! Fruitopia's fruit expert here. Ready to explore the wonderful world of fruits with you. What's on your mind?"
            ],
            "goodbye": [
                "Goodbye! Remember to eat your fruits for better health. Come back anytime!",
                "Take care! Stay healthy and fruity. See you soon!",
                "Farewell! Don't forget that an apple a day keeps the doctor away. Bye!",
                "See you later! Keep enjoying those healthy fruits!"
            ],
            "recommend_fruits": [
                "Based on your health needs, here are some excellent fruit recommendations: {fruits}",
                "For your condition, I recommend these nutrient-rich fruits: {fruits}",
                "These fruits would be particularly beneficial for you: {fruits}",
                "Considering your health goals, try these fruits: {fruits}"
            ],
            "fruit_info": [
                "Here's what I know about {fruit}: {info}",
                "{fruit} is a wonderful fruit! {info}",
                "Let me tell you about {fruit}: {info}",
                "Here's some detailed information about {fruit}: {info}"
            ],
            "quantity_amount": [
                "For optimal health benefits, aim for {amount} of {fruit} per day",
                "A typical serving of {fruit} is {amount}",
                "The recommended daily amount of {fruit} is {amount}",
                "You should consume about {amount} of {fruit} daily"
            ],
            "seasonal_availability": [
                "{fruit} is typically in season during {season}",
                "You can find fresh {fruit} during {season}",
                "{fruit} is at its best and most nutritious when in season: {season}",
                "The peak season for {fruit} is {season}"
            ],
            "recipes_cooking": [
                "Here are some delicious ways to enjoy {fruit}: {recipes}",
                "Try these recipes featuring {fruit}: {recipes}",
                "{fruit} works great in these dishes: {recipes}",
                "Here are some cooking ideas with {fruit}: {recipes}"
            ],
            "allergy_warnings": [
                "Important: {fruit} contains {allergens}. Please consult your doctor if you have allergies",
                "Note: {fruit} may cause reactions in people with {allergens} allergies",
                "Caution: {fruit} contains {allergens} which some people are sensitive to",
                "Please be aware that {fruit} has {allergens} which may affect some individuals"
            ],
            "comparison": [
                "Comparing {fruit1} and {fruit2}: {comparison}",
                "Here's how {fruit1} and {fruit2} stack up: {comparison}",
                "The main differences between {fruit1} and {fruit2}: {comparison}",
                "{fruit1} vs {fruit2}: {comparison}"
            ],
            "storage_preservation": [
                "To keep {fruit} fresh: {storage_tips}",
                "Storage tips for {fruit}: {storage_tips}",
                "Here's how to store {fruit}: {storage_tips}",
                "{fruit} storage guide: {storage_tips}"
            ],
            "fun_facts": [
                "Fun fact about {fruit}: {fact}",
                "Did you know? {fact}",
                "Here's an interesting fact about {fruit}: {fact}",
                "Fun trivia: {fact}"
            ],
            "meal_planning": [
                "Here are some meal ideas featuring {fruit}: {meals}",
                "Try incorporating {fruit} into these meals: {meals}",
                "{fruit} works perfectly in these dishes: {meals}",
                "Meal planning with {fruit}: {meals}"
            ],
            "default": [
                "I'd love to help you with fruit-related questions! Could you please be more specific about what you're looking for?",
                "I'm here to help with all things fruit-related. Could you tell me more about what you need?",
                "I'm your fruit expert! Whether it's nutrition, recipes, or health benefits, I'm here to help. What would you like to know?",
                "Fruitopia has extensive knowledge about fruits. What specific information are you looking for?",
                "I can help with fruit recommendations, nutrition info, recipes, and more. How can I assist you today?"
            ]
        }

        # Save the training data
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump({
                'intents': self.intents,
                'responses': self.responses
            }, f, indent=2, ensure_ascii=False)

        print(f"Created comprehensive training data at {data_path}")

    def classify_intent(self, message: str, threshold: float = 0.2) -> str:
        """Classify the intent of a message using semantic similarity"""
        if not self.intent_embeddings is not None:
            return "default"

        # Preprocess the message
        processed_message = self.preprocess_text(message)

        # Encode the message
        message_embedding = self.model.encode([processed_message])

        # Calculate similarities
        similarities = cosine_similarity(message_embedding, self.intent_embeddings)[0]

        # Find the best match
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]

        if best_similarity >= threshold:
            return self.intent_map[best_idx]
        else:
            return "default"

    def extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract comprehensive entities from the message"""
        entities = {
            'diseases': [],
            'fruits': [],
            'conditions': [],
            'quantities': [],
            'seasons': [],
            'cooking_methods': [],
            'allergens': [],
            'origins': [],
            'comparisons': []
        }

        message_lower = message.lower()

        # Enhanced diseases/health conditions
        diseases = [
            'diabetes', 'diabetic', 'blood sugar', 'high blood pressure', 'hypertension',
            'heart disease', 'cholesterol', 'weight loss', 'obesity', 'cancer',
            'immune system', 'digestion', 'constipation', 'inflammation', 'arthritis',
            'bone health', 'anemia', 'thyroid', 'kidney', 'liver', 'asthma', 'depression',
            'memory', 'brain health', 'skin health', 'hair health', 'eyesight', 'vision',
            'blood pressure', 'high cholesterol', 'heart health', 'digestive health'
        ]

        for disease in diseases:
            if disease in message_lower:
                entities['diseases'].append(disease)

        # Fruit names (from database) - improved matching
        if self.fruit_database:
            for fruit in self.fruit_database.keys():
                fruit_lower = fruit.lower()
                # Check exact match
                if fruit_lower in message_lower:
                    entities['fruits'].append(fruit)
                # Check singular/plural variations
                elif fruit_lower.endswith('s') and fruit_lower[:-1] in message_lower:
                    entities['fruits'].append(fruit)
                elif fruit_lower + 's' in message_lower:
                    entities['fruits'].append(fruit)
                # Check partial matches for common fruits
                elif len(fruit_lower) > 4 and fruit_lower[:-1] in message_lower:  # Remove last char
                    entities['fruits'].append(fruit)

        # Quantity-related keywords
        quantity_keywords = ['how much', 'how many', 'quantity', 'amount', 'serving', 'portion', 'daily']
        for keyword in quantity_keywords:
            if keyword in message_lower:
                entities['quantities'].append(keyword)

        # Seasonal keywords
        season_keywords = ['season', 'available', 'fresh', 'when', 'time', 'month']
        for keyword in season_keywords:
            if keyword in message_lower:
                entities['seasons'].append(keyword)

        # Cooking/recipe keywords
        cooking_keywords = ['recipe', 'cook', 'prepare', 'salad', 'smoothie', 'juice', 'bake', 'grill']
        for keyword in cooking_keywords:
            if keyword in message_lower:
                entities['cooking_methods'].append(keyword)

        # Allergy keywords
        allergy_keywords = ['allergic', 'allergy', 'intolerant', 'sensitive', 'reaction']
        for keyword in allergy_keywords:
            if keyword in message_lower:
                entities['allergens'].append(keyword)

        # Origin/geography keywords
        origin_keywords = ['where', 'from', 'origin', 'country', 'grown', 'cultivated']
        for keyword in origin_keywords:
            if keyword in message_lower:
                entities['origins'].append(keyword)

        # Comparison keywords
        comparison_keywords = ['vs', 'versus', 'better', 'compare', 'difference', 'which']
        for keyword in comparison_keywords:
            if keyword in message_lower:
                entities['comparisons'].append(keyword)

        return entities

    def recommend_fruits_for_condition(self, condition: str) -> List[str]:
        """Recommend fruits based on health condition"""
        if not self.fruit_database:
            return ["apples", "bananas", "oranges"]  # Default recommendations

        recommendations = []

        for fruit_name, fruit_data in self.fruit_database.items():
            # Check health benefits
            health_benefits = fruit_data.get('health_benefits', [])
            benefits_text = ' '.join(health_benefits).lower()

            # Check diseases this fruit helps with
            diseases = fruit_data.get('diseases', [])
            diseases_text = ' '.join(diseases).lower()

            # Simple keyword matching
            condition_lower = condition.lower()
            if (condition_lower in benefits_text or
                condition_lower in diseases_text or
                any(cond in condition_lower for cond in ['diabetes', 'blood pressure', 'heart', 'cholesterol']) and
                any(benefit in benefits_text for benefit in ['blood sugar', 'blood pressure', 'heart', 'cholesterol'])):
                recommendations.append(fruit_name)

        # Return top recommendations or defaults
        if recommendations:
            return recommendations[:5]  # Limit to 5 recommendations
        else:
            return ["apples", "bananas", "oranges", "berries", "citrus fruits"]

    def get_fruit_info(self, fruit_name: str) -> str:
        """Get detailed information about a specific fruit"""
        if not self.fruit_database or fruit_name not in self.fruit_database:
            return f"I'm sorry, I don't have information about {fruit_name}."

        fruit = self.fruit_database[fruit_name]

        info_parts = []

        # Basic info
        if 'description' in fruit:
            info_parts.append(f"Description: {fruit['description']}")

        # Nutritional info
        if 'nutrition' in fruit:
            nutrition = fruit['nutrition']
            nutrition_info = []
            for nutrient, value in nutrition.items():
                if isinstance(value, (int, float)) and value > 0:
                    nutrition_info.append(f"{nutrient}: {value}")
            if nutrition_info:
                info_parts.append(f"Nutrition (per 100g): {', '.join(nutrition_info[:5])}")

        # Health benefits
        if 'health_benefits' in fruit and fruit['health_benefits']:
            benefits = fruit['health_benefits'][:3]  # Limit to 3 benefits
            info_parts.append(f"Health benefits: {', '.join(benefits)}")

        # Best season
        if 'season' in fruit:
            info_parts.append(f"Best season: {fruit['season']}")

        return ' '.join(info_parts) if info_parts else f"{fruit_name} is a healthy fruit with many nutritional benefits!"

    def generate_response(self, message: str) -> str:
        """Generate a comprehensive response to the user's message"""
        # Classify intent
        intent = self.classify_intent(message)

        # Extract entities
        entities = self.extract_entities(message)

        # Generate response based on intent
        if intent == "greet":
            return np.random.choice(self.responses.get("greet", ["Hello!"]))

        elif intent == "goodbye":
            return np.random.choice(self.responses.get("goodbye", ["Goodbye!"]))

        elif intent == "recommend_fruits":
            if entities['diseases']:
                condition = entities['diseases'][0]
                fruits = self.recommend_fruits_for_condition(condition)
                response_template = np.random.choice(self.responses.get("recommend_fruits", ["I recommend: {fruits}"]))
                return response_template.format(fruits=", ".join(fruits))
            else:
                fruits = ["apples", "bananas", "oranges", "berries", "kiwi"]
                response_template = np.random.choice(self.responses.get("recommend_fruits", ["I recommend: {fruits}"]))
                return response_template.format(fruits=", ".join(fruits))

        elif intent == "fruit_info":
            if entities['fruits']:
                fruit = entities['fruits'][0]
                info = self.get_fruit_info(fruit)
                response_template = np.random.choice(self.responses.get("fruit_info", ["{info}"]))
                return response_template.format(fruit=fruit, info=info)
            else:
                return "I'd be happy to tell you about a specific fruit. Which fruit are you interested in?"

        elif intent == "quantity_amount":
            if entities['fruits']:
                fruit = entities['fruits'][0]
                amount = self.get_serving_size(fruit)
                response_template = np.random.choice(self.responses.get("quantity_amount", ["A serving is {amount}"]))
                return response_template.format(fruit=fruit, amount=amount)
            else:
                return "For most fruits, a typical serving is 1 medium piece or 1 cup of sliced fruit."

        elif intent == "seasonal_availability":
            if entities['fruits']:
                fruit = entities['fruits'][0]
                season = self.get_fruit_season(fruit)
                response_template = np.random.choice(self.responses.get("seasonal_availability", ["{season}"]))
                return response_template.format(fruit=fruit, season=season)
            else:
                return "Different fruits are in season at different times. Which fruit are you interested in?"

        elif intent == "recipes_cooking":
            if entities['fruits']:
                fruit = entities['fruits'][0]
                recipes = self.get_fruit_recipes(fruit)
                response_template = np.random.choice(self.responses.get("recipes_cooking", ["Try these: {recipes}"]))
                return response_template.format(fruit=fruit, recipes=recipes)
            else:
                return "I can suggest recipes for specific fruits. Which fruit would you like recipes for?"

        elif intent == "allergy_warnings":
            if entities['fruits']:
                fruit = entities['fruits'][0]
                warnings = self.get_allergy_info(fruit)
                response_template = np.random.choice(self.responses.get("allergy_warnings", ["{allergens}"]))
                return response_template.format(fruit=fruit, allergens=warnings)
            else:
                return "Most fruits are generally safe, but some people may be allergic to certain fruits. Which fruit are you concerned about?"

        elif intent == "comparison":
            if len(entities['fruits']) >= 2:
                fruit1, fruit2 = entities['fruits'][:2]
                comparison = self.compare_fruits(fruit1, fruit2)
                response_template = np.random.choice(self.responses.get("comparison", ["{comparison}"]))
                return response_template.format(fruit1=fruit1, fruit2=fruit2, comparison=comparison)
            else:
                return "To compare fruits, please mention at least two fruits you'd like to compare."

        elif intent == "storage_preservation":
            if entities['fruits']:
                fruit = entities['fruits'][0]
                storage = self.get_storage_tips(fruit)
                response_template = np.random.choice(self.responses.get("storage_preservation", ["{storage_tips}"]))
                return response_template.format(fruit=fruit, storage_tips=storage)
            else:
                return "Storage tips vary by fruit. Which fruit do you need storage advice for?"

        elif intent == "fun_facts":
            if entities['fruits']:
                fruit = entities['fruits'][0]
                fact = self.get_fun_fact(fruit)
                response_template = np.random.choice(self.responses.get("fun_facts", ["{fact}"]))
                return response_template.format(fruit=fruit, fact=fact)
            else:
                return "Fruits have amazing facts! Which fruit would you like to learn something interesting about?"

        elif intent == "meal_planning":
            if entities['fruits']:
                fruit = entities['fruits'][0]
                meals = self.get_meal_ideas(fruit)
                response_template = np.random.choice(self.responses.get("meal_planning", ["{meals}"]))
                return response_template.format(fruit=fruit, meals=meals)
            else:
                return "Fruits work great in many meals! Which fruit would you like meal ideas for?"

        else:
            # Fallback: Check for any entities and respond accordingly
            if entities['fruits']:
                fruit = entities['fruits'][0]
                info = self.get_fruit_info(fruit)
                return f"Let me tell you about {fruit}: {info}"

            elif entities['diseases']:
                condition = entities['diseases'][0]
                fruits = self.recommend_fruits_for_condition(condition)
                return f"For {condition}, I recommend these fruits: {', '.join(fruits)}"

            elif entities['quantities']:
                return "I can help with serving sizes and daily recommendations. Which fruit are you asking about?"

            elif entities['seasons']:
                return "I can tell you when fruits are in season. Which fruit interests you?"

            elif entities['cooking_methods']:
                return "I have many fruit recipes! Which fruit would you like recipes for?"

            elif entities['allergens']:
                return "I can provide allergy information for fruits. Which fruit are you concerned about?"

            elif entities['origins']:
                return "I can tell you about where fruits come from. Which fruit would you like to know about?"

            else:
                return np.random.choice(self.responses.get("default", ["I'm here to help with fruits and health!"]))

    def save_model(self, filepath: str):
        """Save the trained chatbot model"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        model_data = {
            'intents': self.intents,
            'responses': self.responses,
            'intent_map': self.intent_map,
            'intent_embeddings': self.intent_embeddings,
            'model_name': self.model.get_sentence_embedding_dimension()
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"Model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load a trained chatbot model"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)

            self.intents = model_data.get('intents', {})
            self.responses = model_data.get('responses', {})
            self.intent_map = model_data.get('intent_map', [])
            self.intent_embeddings = model_data.get('intent_embeddings')

            print(f"Model loaded from {filepath}")
            return True

        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def get_serving_size(self, fruit_name: str) -> str:
        """Get serving size information for a fruit"""
        if not self.fruit_database or fruit_name not in self.fruit_database:
            return "1 medium piece or 1 cup"

        fruit = self.fruit_database[fruit_name]
        serving = fruit.get('serving_size', fruit.get('serving', '1 medium piece or 1 cup'))
        return serving

    def get_fruit_season(self, fruit_name: str) -> str:
        """Get seasonal availability for a fruit"""
        if not self.fruit_database or fruit_name not in self.fruit_database:
            return "Available year-round in most regions"

        fruit = self.fruit_database[fruit_name]
        season = fruit.get('season', fruit.get('seasons', 'Year-round'))
        return f"{season}"

    def get_fruit_recipes(self, fruit_name: str) -> str:
        """Get recipe suggestions for a fruit"""
        recipes = {
            'apples': 'apple pie, apple sauce, fruit salad, baked apples',
            'bananas': 'smoothies, banana bread, banana splits, fruit salad',
            'oranges': 'orange juice, fruit salad, orange marmalade, citrus salad',
            'berries': 'berry smoothies, fruit salad, berry desserts, yogurt parfaits',
            'kiwi': 'fruit salad, kiwi smoothies, tropical fruit bowls',
            'mango': 'mango salsa, smoothies, tropical salads, mango chutney',
            'pineapple': 'pineapple salsa, tropical salads, grilled pineapple, fruit salad'
        }

        fruit_key = fruit_name.lower()
        if fruit_key in recipes:
            return recipes[fruit_key]
        else:
            return f"{fruit_name} smoothies, {fruit_name} salad, baked {fruit_name}, {fruit_name} desserts"

    def get_allergy_info(self, fruit_name: str) -> str:
        """Get allergy information for a fruit"""
        allergy_info = {
            'strawberries': 'oral allergy syndrome (related to birch pollen)',
            'bananas': 'latex-fruit syndrome',
            'kiwi': 'severe allergic reactions in some individuals',
            'apples': 'oral allergy syndrome',
            'peaches': 'stone fruit allergies',
            'citrus': 'citrus allergies (rare)',
            'berries': 'potential for allergic reactions'
        }

        fruit_key = fruit_name.lower()
        if fruit_key in allergy_info:
            return allergy_info[fruit_key]
        else:
            return "generally well-tolerated, but consult a doctor if you have concerns"

    def compare_fruits(self, fruit1: str, fruit2: str) -> str:
        """Compare two fruits"""
        if not self.fruit_database:
            return f"Both {fruit1} and {fruit2} are healthy fruits with different nutritional profiles."

        info1 = self.get_fruit_info(fruit1)
        info2 = self.get_fruit_info(fruit2)

        return f"{fruit1}: {info1[:100]}... vs {fruit2}: {info2[:100]}..."

    def get_storage_tips(self, fruit_name: str) -> str:
        """Get storage tips for a fruit"""
        storage_tips = {
            'apples': 'Store in refrigerator crisper drawer for up to 1 month',
            'bananas': 'Store at room temperature until ripe, then refrigerate',
            'oranges': 'Store at room temperature for 1-2 weeks',
            'berries': 'Refrigerate and use within 2-3 days',
            'kiwi': 'Store at room temperature until ripe, then refrigerate',
            'mango': 'Store at room temperature until ripe',
            'pineapple': 'Store at room temperature or refrigerate after cutting'
        }

        fruit_key = fruit_name.lower()
        if fruit_key in storage_tips:
            return storage_tips[fruit_key]
        else:
            return "Store in a cool, dry place or refrigerator depending on ripeness"

    def get_fun_fact(self, fruit_name: str) -> str:
        """Get a fun fact about a fruit"""
        fun_facts = {
            'apples': 'There are over 7,500 varieties of apples grown worldwide!',
            'bananas': 'Bananas are technically berries, while strawberries are not!',
            'oranges': 'Oranges are the largest citrus fruit by production volume.',
            'kiwi': 'Kiwis are native to China and were originally called Chinese gooseberries.',
            'mango': 'Mangoes are the national fruit of India, Pakistan, and the Philippines.',
            'pineapple': 'Pineapples take about 2 years to grow and mature.',
            'strawberries': 'Strawberries are the only fruit with seeds on the outside.'
        }

        fruit_key = fruit_name.lower()
        if fruit_key in fun_facts:
            return fun_facts[fruit_key]
        else:
            return f"{fruit_name.capitalize()} is packed with vitamins and nutrients that support good health!"

    def get_meal_ideas(self, fruit_name: str) -> str:
        """Get meal planning ideas for a fruit"""
        meal_ideas = {
            'apples': 'Breakfast: apple slices with peanut butter. Lunch: apple salad. Snack: baked apples.',
            'bananas': 'Breakfast: banana smoothies. Lunch: banana wraps. Snack: banana chips.',
            'oranges': 'Breakfast: orange juice. Lunch: citrus salad. Snack: orange segments.',
            'berries': 'Breakfast: berry yogurt parfait. Lunch: berry salad. Snack: mixed berries.',
            'kiwi': 'Breakfast: kiwi fruit bowl. Lunch: tropical salad. Snack: kiwi slices.',
            'mango': 'Breakfast: mango smoothie. Lunch: mango salsa with fish. Snack: mango slices.',
            'pineapple': 'Breakfast: tropical fruit bowl. Lunch: pineapple salsa. Snack: grilled pineapple.'
        }

        fruit_key = fruit_name.lower()
        if fruit_key in meal_ideas:
            return meal_ideas[fruit_key]
        else:
            return f"Add {fruit_name} to smoothies, salads, desserts, or enjoy as a fresh snack!"

# Global chatbot instance
chatbot = None

def initialize_chatbot():
    """Initialize the chatbot with training data and fruit database"""
    global chatbot
    if chatbot is None:
        chatbot = FruitopiaChatbot()

    # Load fruit database
    chatbot.load_fruit_database()

    # Load training data
    chatbot.load_training_data()

    print("Chatbot initialized successfully!")

def get_response(message: str) -> str:
    """Get a response from the chatbot"""
    return chatbot.generate_response(message)

if __name__ == "__main__":
    # Initialize and test the chatbot
    initialize_chatbot()

    # Test conversations - comprehensive examples
    test_messages = [
        "Hello",
        "Hi there!",
        "I have diabetes, what fruits should I eat?",
        "Tell me about apples",
        "What are the health benefits of bananas?",
        "How much should I eat daily?",
        "When is apple season?",
        "Do you have any recipes with mango?",
        "I'm allergic to strawberries, what should I know?",
        "Which is better: apples or oranges?",
        "How should I store bananas?",
        "Tell me a fun fact about kiwi",
        "What meals can I make with pineapple?",
        "I have high blood pressure",
        "What about oranges?",
        "Goodbye"
    ]

    print("\n🧪 Testing Fruitopia Chatbot:")
    print("=" * 40)

    for message in test_messages:
        response = get_response(message)
        print(f"👤 {message}")
        print(f"🤖 {response}")
        print()