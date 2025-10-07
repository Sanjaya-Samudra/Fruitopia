from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="Fruitopia AI Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Fruit(BaseModel):
    name: str
    tagline: Optional[str]
    image: Optional[str]
    description: Optional[str]
    nutrition: Optional[List[str]]
    benefits: Optional[List[str]]
    serving: Optional[str]
    categories: Optional[List[str]]

# Sample data for demonstration
fruits_db = [
    Fruit(
        name="Blueberries",
        tagline="The Antioxidant Champion",
        image="https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=400&h=300&fit=crop",
        description="Small but mighty, blueberries are packed with anthocyanins, powerful antioxidants that give them their deep blue color and incredible health benefits.",
        nutrition=["Vitamin C: 24% DV", "Vitamin K: 36% DV", "Manganese: 25% DV"],
        benefits=["Improves brain function", "Supports heart health", "Reduces inflammation", "Regulates blood sugar"],
        serving="1 cup (148g) - 84 calories",
        categories=["antioxidant-rich", "immune-boosting"]
    ),
    Fruit(
        name="Avocado",
        tagline="The Heart-Healthy Superfruit",
        image="https://images.unsplash.com/photo-1612215047504-a6c07dbe4f7f?w=500&auto=format&fit=crop&q=60",
        description="Rich in monounsaturated fats, avocados support heart health while providing essential nutrients and helping your body absorb fat-soluble vitamins.",
        nutrition=["Folate: 20% DV", "Potassium: 14% DV", "Fiber: 10g"],
        benefits=["Supports cardiovascular health", "Aids nutrient absorption", "Reduces cholesterol", "Weight management"],
        serving="1/2 medium avocado (100g) - 160 calories",
        categories=["heart-healthy"]
    ),
    # Add more fruits as needed
]

@app.get("/fruits", response_model=List[Fruit])
def get_fruits(category: Optional[str] = Query(None)):
    if category and category != "all":
        return [fruit for fruit in fruits_db if category in (fruit.categories or [])]
    return fruits_db

@app.get("/fruits/{fruit_name}", response_model=Fruit)
def get_fruit_detail(fruit_name: str):
    for fruit in fruits_db:
        if fruit.name.lower() == fruit_name.lower():
            return fruit
    return None

# --- Recommendation Endpoint ---
from fastapi import Body
@app.post("/recommend")
def recommend_fruits(disease: str = Body(..., embed=True)):
    # Dummy logic: filter fruits by disease in categories
    recommended = [fruit for fruit in fruits_db if disease.lower() in (fruit.categories or [])]
    return {"recommended": recommended}

# --- NLP Extraction Endpoint ---
import sys
sys.path.append("./nlp")
from nlp_pipeline import extract_diseases
@app.post("/nlp/extract")
def nlp_extract(text: str = Body(..., embed=True)):
    diseases = extract_diseases(text)
    return {"diseases": diseases}

# --- Image Recognition Endpoint ---
sys.path.append("./vision")
from vision.image_recognition import identify_fruit
from fastapi import UploadFile, File as FastAPIFile
@app.post("/vision/identify")
async def vision_identify(image: UploadFile = FastAPIFile(...)):
    # Save uploaded file temporarily
    temp_path = f"temp_{image.filename}"
    with open(temp_path, "wb") as f:
        f.write(await image.read())
    fruit_name = identify_fruit(temp_path)
    return {"fruit": fruit_name}

# --- Chatbot Endpoint ---
sys.path.append("./chatbot")
from chatbot import get_response
@app.post("/chatbot/message")
def chatbot_message(message: str = Body(..., embed=True)):
    response = get_response(message)
    return {"response": response}
