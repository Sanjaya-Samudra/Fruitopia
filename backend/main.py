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

# --- NLP Extraction Endpoint ---
import sys
import os
# Add the backend directory to the path for relative imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(backend_dir, 'nlp'))
try:
    from nlp_pipeline import extract_diseases  # type: ignore
except ImportError:
    print("Warning: nlp_pipeline not available")
    def extract_diseases(text): return []
from fastapi import Body
@app.post("/nlp/extract")
def nlp_extract(text: str = Body(..., embed=True)):
    diseases = extract_diseases(text)
    return {"diseases": diseases}

# --- Image Recognition Endpoint ---
sys.path.insert(0, os.path.join(backend_dir, 'vision'))
try:
    from vision.image_recognition import identify_fruit
except ImportError:
    print("Warning: vision module not available")
    def identify_fruit(image_path): return 'unknown'
from fastapi import UploadFile, File
@app.post("/vision/identify")
async def vision_identify(image: UploadFile = File(...)):
    # Save uploaded file temporarily
    temp_path = f"temp_{image.filename}"
    with open(temp_path, "wb") as f:
        f.write(await image.read())
    fruit_name = identify_fruit(temp_path)
    return {"fruit": fruit_name}

# --- Chatbot Endpoint ---
import requests
from uuid import uuid4
# Add chatbot directory to path
sys.path.append(os.path.join(backend_dir, 'chatbot'))

# Initialize the custom chatbot on startup
chatbot_initialized = False
initialize_chatbot_func = None
get_response_func = None

def init_chatbot():
    global chatbot_initialized, get_response_func
    if not chatbot_initialized:
        try:
            from custom_chatbot import initialize_chatbot as init_func, get_response as response_func  # type: ignore
            init_func()
            get_response_func = response_func
            chatbot_initialized = True
            print("Chatbot initialized successfully")
        except Exception as e:
            print(f"Chatbot initialization failed: {e}")
            get_response_func = lambda msg: "I'm sorry, I'm having trouble processing your request right now."

# In-memory session storage (for demo; use Redis/DB in production)
chat_sessions = {}

@app.post("/chatbot/message")
def chatbot_message(message: str = Body(..., embed=True), session_id: Optional[str] = Body(None, embed=True)):
    # Initialize chatbot if not already done
    if not chatbot_initialized:
        init_chatbot()
        
    if not session_id:
        session_id = str(uuid4())

    # Initialize session if new
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {"history": []}

    # Get response from custom chatbot
    try:
        bot_response = get_response_func(message)
    except Exception as e:
        print(f"Chatbot error: {e}")
        bot_response = "I'm sorry, I'm having trouble processing your request right now."

    # Update session history
    chat_sessions[session_id]["history"].append({"user": message, "bot": bot_response})

    return {"response": bot_response, "session_id": session_id}
