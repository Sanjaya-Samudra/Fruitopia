"""Fruitopia AI Platform - Production Backend"""

import json, os, logging, difflib, sys, math
from pathlib import Path
from typing import Optional, List, Dict
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

FILE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FILE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "FruitImageDataset"

sys.path.insert(0, str(FILE_DIR))
sys.path.insert(0, str(FILE_DIR / "services"))

from services.recommender import get_recommendations, DISEASES_EXTENDED
from services.fruit_service import fruit_service
from services.usda_api import usda_client
from nlp.nlp_pipeline import extract_all_entities

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("fruitopia")

try:
    env_path = FILE_DIR / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for ln in f:
                ln = ln.strip()
                if not ln or ln.startswith("#") or "=" not in ln:
                    continue
                k, v = ln.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
except Exception:
    pass

app = FastAPI(title="Fruitopia AI Platform", version="2.0.0",
              description="AI-Powered Intelligent Fruit Recommendation System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Lazy Model Loading ----
_MODEL = None
_MODEL_CLASSES = None

def _ensure_model():
    global _MODEL, _MODEL_CLASSES
    if _MODEL is not None:
        return
    try:
        model_path = PROJECT_ROOT / "ml" / "models" / "fruit_classifier.best.pt"
        if not model_path.exists():
            model_path = PROJECT_ROOT / "ml" / "models" / "fruit_classifier.pt"
        if not model_path.exists():
            logger.info("No model file found")
            return
        import torch, torch.nn as nn
        from torchvision import models
        data = torch.load(str(model_path), map_location="cpu")
        classes = data.get("classes")
        if not classes or "model_state" not in data:
            return
        model = models.mobilenet_v2(pretrained=False)
        model.classifier[1] = nn.Linear(model.last_channel, len(classes))
        model.load_state_dict(data["model_state"])
        model.eval()
        _MODEL = model
        _MODEL_CLASSES = classes
        logger.info(f"Model loaded with {len(classes)} classes")
    except Exception as e:
        logger.info(f"Model load skipped: {e}")

@app.on_event("startup")
def _startup():
    _ensure_model()

# ============================================================
#  FRUIT EXPLORE & DATABASE ENDPOINTS
# ============================================================

@app.get("/fruits")
def list_fruits():
    return {"fruits": fruit_service.get_all_fruits(), "total": fruit_service.get_fruit_count()}

@app.get("/fruits/search")
def search_fruits(q: str = Query("", alias="q")):
    if not q:
        return {"results": fruit_service.get_all_fruits()[:10]}
    results = fruit_service.search_fruits(q)
    return {"query": q, "results": results}

@app.get("/fruits/search/benefit")
def search_by_benefit(benefit: str = Query("", alias="b")):
    results = fruit_service.search_by_benefit(benefit)
    return {"benefit": benefit, "results": results}

@app.get("/fruits/seasonality")
def fruit_seasonality():
    return {"seasonality": fruit_service.get_fruit_seasonality()}

@app.get("/fruits/{slug}")
def get_fruit(slug: str):
    if slug in ("search", "seasonality"):
        raise HTTPException(status_code=404, detail="Invalid fruit name")
    fruit = fruit_service.get_fruit(slug)
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    return fruit

@app.get("/fruits/{slug}/nutrition")
def get_fruit_nutrition(slug: str):
    fruit = fruit_service.get_fruit(slug)
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    nutrition = fruit.get("nutritionalFacts", {})
    health = fruit.get("healthBenefits", [])
    return {"fruit": slug, "nutrition": nutrition, "health_benefits": health}

@app.get("/fruits/{slug}/usda")
def get_usda_nutrition(slug: str):
    data = usda_client.search_by_fruit_name(slug)
    return data

# ============================================================
#  RECOMMENDATION ENGINE ENDPOINTS
# ============================================================

@app.get("/recommend/diseases")
def recommend_diseases_list():
    return {"diseases": sorted(DISEASES_EXTENDED.keys()), "total": len(DISEASES_EXTENDED)}

@app.get("/recommend/diseases/{disease}")
def recommend_disease_detail(disease: str):
    info = DISEASES_EXTENDED.get(disease)
    if not info:
        raise HTTPException(status_code=404, detail="Disease not found")
    return {"disease": disease, "info": info}

@app.post("/recommend")
def recommend_fruits(payload: dict):
    disease = payload.get("disease", payload.get("text", "")).strip()
    have = payload.get("have", [])
    if isinstance(have, str):
        have = [h.strip() for h in have.split(",") if h.strip()]
    result = get_recommendations(disease, have)
    if not result["recommendations"]:
        entities = extract_all_entities(disease)
        if entities["diseases"]:
            result = get_recommendations(entities["diseases"][0], have)
    return result

@app.post("/recommend/natural")
def recommend_from_natural(text: str = Body(..., embed=True)):
    entities = extract_all_entities(text)
    disease = entities["diseases"][0] if entities["diseases"] else "general"
    fruits = entities.get("fruits", [])
    result = get_recommendations(disease, have=fruits)
    result["entities"] = entities
    return result

# ============================================================
#  NLP ENDPOINTS
# ============================================================

@app.post("/nlp/extract")
def nlp_extract(text: str = Body(..., embed=True)):
    entities = extract_all_entities(text)
    return entities

# ============================================================
#  CHATBOT ENDPOINT - RAG Pipeline
# ============================================================

chatbot_initialized = False
get_response_func = None

def init_chatbot():
    global chatbot_initialized, get_response_func
    if chatbot_initialized:
        return
    try:
        sys.path.append(str(FILE_DIR / "chatbot"))
        from custom_chatbot import initialize_chatbot as init_func, get_response as resp_func
        init_func()
        get_response_func = resp_func
        chatbot_initialized = True
        logger.info("Chatbot initialized")
    except Exception as e:
        logger.error(f"Chatbot init failed: {e}")

chat_sessions: Dict[str, dict] = {}

@app.post("/chatbot/message")
def chatbot_message(message: str = Body(..., embed=True), session_id: Optional[str] = Body(None, embed=True)):
    if not chatbot_initialized:
        init_chatbot()
    if not session_id:
        session_id = str(uuid4())
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {"history": []}
    try:
        bot_response = get_response_func(message) if get_response_func else "I'm ready to help with fruit questions!"
    except Exception:
        bot_response = "I'm having trouble processing your request."
    chat_sessions[session_id]["history"].append({"user": message, "bot": bot_response})
    return {"response": bot_response, "session_id": session_id}

# ============================================================
#  RECIPE GENERATOR
# ============================================================

RECIPE_TEMPLATES = {
    "detox": {
        "title": "Fruit Detox Bowl",
        "tagline": "Cleanse and refresh with antioxidant-rich fruits",
    },
    "energy": {
        "title": "Energizing Fruit Smoothie",
        "tagline": "Natural energy boost from vitamin-packed fruits",
    },
    "immunity": {
        "title": "Immunity Booster Fruit Salad",
        "tagline": "Strengthen your immune system with vitamin C rich fruits",
    },
    "protein": {
        "title": "Protein-Packed Fruit Parfait",
        "tagline": "Post-workout recovery with fruits and protein",
    },
}

@app.post("/recipes/generate")
def generate_recipe(
    fruits: list = Body(..., embed=True),
    dietary_preferences: Optional[list] = Body(None, embed=True),
    cuisine_type: Optional[str] = Body(None, embed=True),
    meal_type: Optional[str] = Body(None, embed=True),
):
    if not fruits:
        raise HTTPException(status_code=400, detail="At least one fruit required")
    primary = fruits[0].lower()
    fruit_data = fruit_service.get_fruit(primary)

    recipe_type = "immunity"
    if dietary_preferences:
        prefs_lower = [p.lower() for p in dietary_preferences]
        if "detox" in prefs_lower or "cleanse" in prefs_lower:
            recipe_type = "detox"
        elif "energy" in prefs_lower or "pre-workout" in prefs_lower:
            recipe_type = "energy"
        elif "protein" in prefs_lower or "post-workout" in prefs_lower:
            recipe_type = "protein"

    template = RECIPE_TEMPLATES.get(recipe_type, RECIPE_TEMPLATES["immunity"])

    suggestion = {"recipe": template["title"], "tagline": template["tagline"], "fruit": primary}

    if fruit_data:
        benefits = fruit_data.get("healthBenefits", [])[:2]
        col = fruit_data.get("appearance", {}).get("colors", ["green"])[0]
        suggestion["benefits"] = benefits
        suggestion["color"] = col

    if dietary_preferences:
        suggestion["dietary"] = dietary_preferences
    if meal_type:
        suggestion["meal_type"] = meal_type
    if cuisine_type:
        suggestion["cuisine"] = cuisine_type
    suggestion["suggested_pairings"] = fruit_data.get("culinaryInformation", {}).get("pairings", []) if fruit_data else []

    return suggestion

# ============================================================
#  VISION / IMAGE RECOGNITION
# ============================================================

@app.get("/vision/health")
def vision_health():
    _ensure_model()
    return {"ok": True, "model_loaded": _MODEL is not None}

@app.get("/vision/classes")
def vision_classes():
    classes = []
    if DATA_DIR.exists():
        classes = sorted([p.name for p in DATA_DIR.iterdir() if p.is_dir()])
    return {"classes": classes}

@app.get("/vision/samples")
def vision_samples(class_name: str = Query(..., alias="cls"), n: int = Query(6, alias="n")):
    cls_dir = DATA_DIR / class_name
    if not cls_dir.exists():
        return {"samples": []}
    files = sorted([p.name for p in cls_dir.iterdir() if p.is_file()])
    return {"samples": files[:n]}

@app.get("/vision/image")
def vision_image(class_name: str = Query(..., alias="cls"), filename: str = Query(..., alias="file")):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="invalid filename")
    fpath = DATA_DIR / class_name / filename
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(str(fpath))

@app.post("/vision/predict")
async def predict_fruit(file: Optional[UploadFile] = File(None), image: Optional[UploadFile] = File(None)):
    upload = file or image
    if not upload:
        return JSONResponse({"error": "no file uploaded"}, status_code=422)
    try:
        tmp_dir = FILE_DIR / "tmp"
        tmp_dir.mkdir(exist_ok=True)
        tmp_path = tmp_dir / (getattr(upload, "filename", "upload.jpg"))
        with open(tmp_path, "wb") as f:
            f.write(await upload.read())
    except Exception as e:
        return JSONResponse({"error": f"failed to save: {e}"}, status_code=500)

    try:
        _ensure_model()
        if _MODEL is not None:
            try:
                import torch
                from torchvision import transforms
                from PIL import Image
                transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                ])
                img = Image.open(str(tmp_path)).convert("RGB")
                tensor = transform(img).unsqueeze(0)
                with torch.no_grad():
                    outputs = _MODEL(tensor)
                    probs = torch.softmax(outputs, dim=1).squeeze(0)
                    topk = torch.topk(probs, k=min(5, probs.numel()))
                    preds = []
                    for idx, score in zip(topk.indices.tolist(), topk.values.tolist()):
                        cls_name = _MODEL_CLASSES[idx] if _MODEL_CLASSES and idx < len(_MODEL_CLASSES) else str(idx)
                        preds.append({"class": cls_name, "score": float(score), "confidence": f"{score*100:.1f}%"})
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
                return JSONResponse({"predictions": preds, "source": "torch-model"})
            except Exception as e:
                logger.info(f"Torch inference failed: {e}")

        try:
            from vision.image_recognition import identify_fruit
            res = identify_fruit(str(tmp_path))
            preds = []
            if isinstance(res, str):
                preds = [{"class": res, "score": 0.9, "confidence": "90.0%"}]
            elif isinstance(res, list):
                preds = [{"class": r[0], "score": float(r[1]), "confidence": f"{float(r[1])*100:.1f}%"} if isinstance(r, (list, tuple)) else {"class": r, "score": 0.9} for r in res]
            elif isinstance(res, dict):
                preds = res.get("predictions", [])
            try:
                tmp_path.unlink()
            except Exception:
                pass
            return JSONResponse({"predictions": preds, "source": "local-identify"})
        except Exception:
            pass

        try:
            tmp_path.unlink()
        except Exception:
            pass
        return JSONResponse({"error": "model not available"}, status_code=501)
    except Exception as e:
        logger.error(f"Predict error: {e}")
        try:
            tmp_path.unlink()
        except Exception:
            pass
        return JSONResponse({"error": "internal error"}, status_code=500)

# ============================================================
#  USDA INTEGRATION ENDPOINTS
# ============================================================

@app.get("/usda/search")
def usda_search(query: str = Query(..., alias="q")):
    return usda_client.search_foods(query)

@app.get("/usda/fruit/{fruit_name}")
def usda_fruit(fruit_name: str):
    return usda_client.search_by_fruit_name(fruit_name)

# ============================================================
#  HEALTH & DISEASE EDUCATION
# ============================================================

@app.get("/health/conditions")
def health_conditions():
    return {"conditions": [
        {"id": k, "name": k.replace("_", " ").title(),
         "severity": v.get("severity", "medium"),
         "category": v.get("category", "general"),
         "synonyms": v.get("synonyms", [])[:3]}
        for k, v in DISEASES_EXTENDED.items()
    ]}

# ============================================================
#  ROOT / INFO
# ============================================================

@app.get("/")
def root():
    return {
        "app": "Fruitopia AI Platform",
        "version": "2.0.0",
        "endpoints": {
            "fruits": "/fruits",
            "fruits_search": "/fruits/search?q=",
            "recommend": "/recommend",
            "recommend_natural": "/recommend/natural",
            "chatbot": "/chatbot/message",
            "vision_predict": "/vision/predict",
            "vision_classes": "/vision/classes",
            "nlp_extract": "/nlp/extract",
            "usda_search": "/usda/search?q=",
            "recipes": "/recipes/generate",
            "health_conditions": "/health/conditions",
        },
    }
