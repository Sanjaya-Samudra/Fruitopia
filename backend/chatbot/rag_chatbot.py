"""RAG (Retrieval-Augmented Generation) Chatbot for Fruitopia

Uses the fruit encyclopedia as a knowledge base with vector search + LLM for natural,
factual responses. Falls back gracefully if no LLM API key is configured.
"""

import os, json, re, time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np

FILE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FILE_DIR.parent.parent
EXPLORE_DIR = PROJECT_ROOT / "data" / "explore"
CACHE_DIR = PROJECT_ROOT / "data" / "usda_cache"

os.makedirs(CACHE_DIR, exist_ok=True)


class VectorStore:
    """Simple in-memory vector store with cosine similarity search."""

    def __init__(self):
        self.documents: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None
        self.embedding_model = None

    def _lazy_load_model(self):
        if self.embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                print(f"Embedding model load failed: {e}")
                return False
        return True

    def add_documents(self, docs: List[Dict]):
        self.documents.extend(docs)

    def build_index(self):
        if not self._lazy_load_model():
            return False
        texts = [d.get("text", "") for d in self.documents]
        if not texts:
            return False
        self.embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return True

    def search(self, query: str, k: int = 5) -> List[Dict]:
        if self.embeddings is None or len(self.documents) == 0:
            return []

        if not self._lazy_load_model():
            return []

        query_emb = self.embedding_model.encode([query], show_progress_bar=False)
        from sklearn.metrics.pairwise import cosine_similarity
        sims = cosine_similarity(query_emb, self.embeddings)[0]
        top_indices = np.argsort(sims)[-k:][::-1]

        results = []
        for idx in top_indices:
            doc = dict(self.documents[idx])
            doc["score"] = float(sims[idx])
            results.append(doc)
        return results


class FruitKnowledgeBase:
    """Builds and maintains the fruit knowledge base from encyclopedia JSONs."""

    def __init__(self):
        self.vector_store = VectorStore()
        self.fruit_names: List[str] = []

    def build(self):
        if not EXPLORE_DIR.exists():
            print(f"Knowledge base dir {EXPLORE_DIR} not found")
            return False

        docs = []
        for json_file in sorted(EXPLORE_DIR.glob("*.json")):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                fruit_name = data.get("fruitName", json_file.stem)
                self.fruit_names.append(fruit_name.lower())

                sections = [
                    ("General", data.get("description", "")),
                    ("Nutrition", self._format_nutrition(data.get("nutritionalFacts", {}))),
                    ("Health Benefits", "; ".join(data.get("healthBenefits", []))),
                    ("Allergies", self._format_allergies(data.get("possibleAllergies", {}))),
                    ("Medical", self._format_medical(data.get("medicalAndDietaryConsiderations", {}))),
                    ("Storage", f"Season: {data.get('storageAndShelfLife', {}).get('seasonAvailability', 'N/A')}. Tips: {data.get('storageAndShelfLife', {}).get('storageTips', 'N/A')}"),
                    ("Culinary", f"Taste: {data.get('culinaryInformation', {}).get('tasteProfile', 'N/A')}. Cooking: {', '.join(data.get('culinaryInformation', {}).get('cookingMethods', []))}"),
                    ("Facts", "; ".join(data.get("funFacts", []) or data.get("uniqueFacts", []))),
                    ("Warnings", "; ".join(data.get("warnings", []))),
                    ("Cultivation", f"Origin: {data.get('origin', 'N/A')}. Growing: {data.get('cultivation', {}).get('growingConditions', 'N/A')}"),
                ]

                for section_name, content in sections:
                    if content and len(content) > 10:
                        doc_text = f"{fruit_name} - {section_name}: {content}"
                        docs.append({
                            "text": doc_text,
                            "fruit": fruit_name.lower(),
                            "section": section_name,
                            "source": json_file.name,
                        })

            except Exception as e:
                print(f"Error loading {json_file}: {e}")

        self.vector_store.add_documents(docs)
        success = self.vector_store.build_index()
        print(f"Knowledge base: {len(docs)} chunks from {len(self.fruit_names)} fruits")
        return success

    def _format_nutrition(self, n: Dict) -> str:
        if not n:
            return ""
        parts = []
        if n.get("calories_kcal"):
            parts.append(f"{n['calories_kcal']} calories per serving")
        for k in ["macronutrients"]:
            if n.get(k):
                for sub, val in n[k].items():
                    if val:
                        parts.append(f"{sub}: {val}{'g' if 'mg' not in str(sub) else ''}")
        return "; ".join(parts[:8])

    def _format_allergies(self, a: Dict) -> str:
        if not a:
            return ""
        return f"Allergens: {', '.join(a.get('allergens', []))}. Symptoms: {', '.join(a.get('symptoms', []))}. Cross-reactivity: {', '.join(a.get('crossReactivity', []))}"

    def _format_medical(self, m: Dict) -> str:
        if not m:
            return ""
        parts = []
        if m.get("beneficialForDiseases"):
            for b in m["beneficialForDiseases"]:
                parts.append(f"Beneficial for {b.get('disease')}: {b.get('reason', '')}")
        if m.get("notRecommendedForDiseases"):
            for b in m["notRecommendedForDiseases"]:
                parts.append(f"Caution for {b.get('disease')}: {b.get('reason', '')}")
        return "; ".join(parts[:4])

    def search(self, query: str, k: int = 5) -> List[Dict]:
        return self.vector_store.search(query, k)

    def get_context_for_query(self, query: str, k: int = 5) -> Tuple[str, List[Dict]]:
        results = self.search(query, k)
        if not results:
            return "", []

        query_lower = query.lower()
        fruit_boost = {}
        for i, r in enumerate(results):
            fruit = r.get("fruit", "")
            section = r.get("section", "")
            boost = 0.0
            if fruit and fruit.strip("s") in query_lower:
                boost += 2.0
            if fruit and fruit in query_lower:
                boost += 1.0
            if section and section.lower() in ("general", "nutrition") and ("what" in query_lower or "about" in query_lower or "tell" in query_lower):
                boost += 0.5
            if section and section.lower() == "nutrition" and any(w in query_lower for w in ["calorie", "nutrition", "vitamin", "mineral", "protein", "fat", "carb"]):
                boost += 1.5
            if section and section.lower() == "health benefits" and any(w in query_lower for w in ["health", "benefit", "good for", "prevent"]):
                boost += 1.5
            if section and section.lower() == "storage" and any(w in query_lower for w in ["season", "available", "when", "store"]):
                boost += 1.5
            if section and section.lower() == "culinary" and any(w in query_lower for w in ["recipe", "cook", "eat", "prepare", "taste"]):
                boost += 1.5
            fruit_boost[fruit] = r["score"] + boost

        results.sort(key=lambda x: fruit_boost.get(x.get("fruit", ""), x["score"]), reverse=True)

        context_parts = []
        seen_fruits = set()
        seen_sections = set()
        for r in results:
            fruit = r.get("fruit", "")
            section = r.get("section", "")
            key = f"{fruit}-{section}"
            if key not in seen_sections:
                context_parts.append(r["text"])
                seen_fruits.add(fruit)
                seen_sections.add(key)

        context = "\n\n".join(context_parts[:k])
        return context, results

    def get_fruit_summaries(self) -> str:
        summaries = []
        for name in sorted(self.fruit_names):
            summaries.append(f"- {name.title()}")
        return "\n".join(summaries)


class RAGChatbot:
    """LLM-powered RAG chatbot with graceful fallback."""

    def __init__(self):
        self.knowledge_base = FruitKnowledgeBase()
        self.llm_available = False
        self.llm_type = None
        self._init_llm()

    def _init_llm(self):
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if openai_key:
            self.llm_available = True
            self.llm_type = "openai"
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=openai_key)
                print("RAG Chatbot: OpenAI LLM initialized")
            except Exception:
                self.llm_available = False

    def generate_response(self, message: str) -> str:
        message_lower = message.lower().strip()

        greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "howdy"]
        if message_lower in greetings or message_lower in [g + " there" for g in greetings]:
            return "Hello! I'm your Fruitopia AI nutrition assistant powered by our fruit knowledge base. I can answer questions about any of our 30+ fruits including their nutrition, health benefits, recipes, seasonal availability, and more. What would you like to explore?"

        if message_lower in ("bye", "goodbye", "see you", "farewell", "thanks", "thank you"):
            return "You're welcome! Remember, eating a variety of colorful fruits every day is the key to optimal nutrition. Come back anytime you need fruit advice!"

        context, sources = self.knowledge_base.get_context_for_query(message, k=4)

        if not context:
            return self._fallback_response(message)

        if self.llm_available and self.llm_type == "openai":
            return self._llm_response(message, context, sources)
        else:
            return self._template_response(message, context, sources)

    def _llm_response(self, message: str, context: str, sources: List[Dict]) -> str:
        try:
            fruit_list = self.knowledge_base.get_fruit_summaries()
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"""You are Fruitopia AI, a friendly nutrition expert assistant.
You have access to a fruit knowledge base with detailed information about 30+ fruits.
Answer the user's question based ONLY on the context provided. If the context doesn't contain enough information, say so.

Available fruits: {fruit_list}

Keep responses concise, informative, and friendly. Include specific nutrient facts when relevant.
Never make up medical claims. Always suggest consulting a doctor for medical advice."""},
                    {"role": "user", "content": f"Context from fruit database:\n{context}\n\nUser question: {message}"}
                ],
                temperature=0.3,
                max_tokens=500,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM call failed: {e}")
            return self._template_response(message, context, sources)

    def _template_response(self, message: str, context: str, sources: List[Dict]) -> str:
        fruits_in_context = list(set(r.get("fruit", "").title() for r in sources if r.get("fruit")))
        fruit_names = ", ".join(fruits_in_context[:3])

        if "recommend" in message or "good for" in message or "disease" in message or "health" in message or "condition" in message:
            recs = self._get_recommendations(message)
            if recs:
                return f"Based on your query, here are fruits worth considering:\n\n{recs}\n\nWould you like more details about any of these?"
            if fruit_names:
                return f"Here's what I found about {fruit_names}: {context[:300]}"
            return "I can help with fruit recommendations! Tell me about your health condition or what benefits you're looking for."

        if "calorie" in message or "nutrition" in message or "vitamin" in message:
            if fruit_names:
                info = "\n".join(fruits_in_context[:2])
                return f"Here's what I found about {info}:\n\n{context[:500]}\n\nWould you like more specific nutritional data?"

        if "recipe" in message or "cook" in message or "eat" in message:
            if fruit_names:
                return f"Great question about {fruit_names}! {context[:400]}"
            return "I have recipe ideas for many fruits! Which fruit are you interested in cooking with?"

        if "season" in message or "available" in message or "when" in message:
            if fruit_names:
                return f"About {fruit_names}: {context[:400]}"
            return "Different fruits peak in different seasons. Which fruit are you interested in?"

        if context:
            return f"Here's what I know:\n\n{context[:500]}"
        return self._fallback_response(message)

    def _get_recommendations(self, message: str) -> str:
        try:
            sys.path.insert(0, str(FILE_DIR.parent))
            from services.recommender import get_recommendations
            from nlp.nlp_pipeline import extract_diseases
            diseases = extract_diseases(message)
            if diseases:
                disease = diseases[0]
                result = get_recommendations(disease)
                recs = result.get("recommendations", [])
                if recs:
                    lines = [f"**For {disease.replace('_', ' ').title()}:**"]
                    for r in recs:
                        cls = r.get("class", "").title()
                        reason = r.get("reason", "")
                        evidence = r.get("evidence", "")
                        line = f"🥝 {cls}: {reason}"
                        if evidence and evidence != "General":
                            line += f" ({evidence})"
                        lines.append(line)
                    return "\n".join(lines)
        except Exception:
            pass
        return ""

    def _fallback_response(self, message: str) -> str:
        message_lower = message.lower()
        if any(w in message_lower for w in ["fruit", "apple", "banana", "orange", "berry"]):
            return "I have detailed information about all our fruits! Could you ask a more specific question about nutrition, health benefits, recipes, or seasonal availability?"
        if any(w in message_lower for w in ["health", "disease", "condition", "symptom"]):
            return "I can help match fruits to your health needs! Tell me about your condition (e.g., diabetes, heart health, inflammation) and I'll recommend specific fruits backed by nutritional science."
        return "I'm your Fruitopia AI assistant! I can answer questions about 30+ fruits - their nutrition, health benefits, recipes, seasonal availability, storage tips, and more. What fruit topic interests you?"


rag_chatbot = None


def initialize():
    global rag_chatbot
    if rag_chatbot is None:
        try:
            rag_chatbot = RAGChatbot()
            rag_chatbot.knowledge_base.build()
            print("RAG Chatbot initialized successfully!")
        except Exception as e:
            print(f"RAG Chatbot initialization failed: {e}")
            rag_chatbot = None


def get_response(message: str) -> str:
    if rag_chatbot is None:
        initialize()
    if rag_chatbot is None:
        return "I'm sorry, I'm having trouble accessing my knowledge base right now. Please try again in a moment."
    return rag_chatbot.generate_response(message)


if __name__ == "__main__":
    initialize()
    tests = [
        "Hello, what fruits do you know about?",
        "Tell me about apples",
        "What fruits are good for diabetes?",
        "How many calories in a banana?",
        "When are strawberries in season?",
        "Do you have recipes with mango?",
        "I have high blood pressure, what should I eat?",
        "Tell me a fun fact about kiwifruit",
        "Thank you, goodbye!",
    ]
    print("\n--- Testing RAG Chatbot ---\n")
    for msg in tests:
        resp = get_response(msg)
        print(f"Q: {msg}")
        print(f"A: {resp[:200]}...")
        print()
