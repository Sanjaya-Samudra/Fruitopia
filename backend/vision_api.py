"""Clean, minimal Fruitopia backend module.

This file exposes only the endpoints the frontend needs and avoids optional
heavy dependencies so it imports reliably. Once this is stable we can
add guarded model loading separately.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
from typing import Optional
import json
import os
import logging
import math
import difflib
import sys
from uuid import uuid4

# Add backend directory to Python path for relative imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

FILE_DIR = Path(__file__).resolve().parent  # backend/
PROJECT_ROOT = FILE_DIR.parent
# initialize logger early so .env loader can use it
logger = logging.getLogger('vision_api')
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)
# Optional .env loader: if a file named backend/.env exists, load simple KEY=VALUE pairs into os.environ.
try:
    env_path = FILE_DIR / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as envf:
            for ln in envf:
                ln = ln.strip()
                if not ln or ln.startswith('#') or '=' not in ln:
                    continue
                k, v = ln.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k:
                    os.environ.setdefault(k, v)
        logger.info(f"Loaded environment overrides from {env_path}")
except Exception:
    logger.info('Failed to load backend/.env (ignored)')
DATA_DIR = PROJECT_ROOT / 'data' / 'FruitImageDataset'
RECS_FILE = FILE_DIR / 'ml' / 'disease_recs.json'
SYN_FILE = FILE_DIR / 'ml' / 'disease_synonyms.json'
META_FILE = FILE_DIR / 'ml' / 'metadata.json'

app = FastAPI(title='Fruitopia - clean backend')


@app.on_event('startup')
def _startup_load_model():
    try:
        _ensure_model()
        if _MODEL is not None:
            logger.info('startup: torch model is loaded and ready')
        else:
            logger.info('startup: torch model not loaded (will use fallback)')
    except Exception:
        logger.exception('startup: unexpected error while loading model')

# Development CORS: allow Angular dev server to call this API
app.add_middleware(
    CORSMiddleware,
    # Allow both common dev-server hostnames so the frontend can call the API
    # whether the browser uses 'localhost' or '127.0.0.1'.
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_json_safe(path: Path) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _get_available_classes() -> list:
    if META_FILE.exists():
        try:
            with open(META_FILE, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                classes = meta.get('classes', [])
                if classes:
                    return sorted(classes)
        except Exception:
            pass
    if DATA_DIR.exists():
        return sorted([p.name for p in DATA_DIR.iterdir() if p.is_dir()])
    return []


def _env_flag(key: str) -> bool:
    """Return True if environment variable 'key' is set to a truthy value, or if backend/.env contains it.
    This is tolerant to being imported in worker processes that may not inherit parent env settings.
    """
    val = os.environ.get(key)
    if val is not None:
        return val in ('1', 'true', 'True', 'yes', 'on')
    # fallback: try to read backend/.env
    try:
        env_path = FILE_DIR / '.env'
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln or ln.startswith('#') or '=' not in ln:
                        continue
                    k, v = ln.split('=', 1)
                    if k.strip() == key:
                        vv = v.strip().strip('"').strip("'")
                        return vv in ('1', 'true', 'True', 'yes', 'on')
    except Exception:
        pass
    return False


# Lazy model state
_MODEL = None
_MODEL_CLASSES = None

def _ensure_model():
    """Attempt to lazily load a PyTorch model saved by ml/train.py at ml/models/fruit_classifier.pt.
    This function swallows import errors so the server remains usable without torch.
    """
    global _MODEL, _MODEL_CLASSES
    if _MODEL is not None:
        return
    try:
        model_path = PROJECT_ROOT / 'ml' / 'models' / 'fruit_classifier.pt'
        if not model_path.exists():
            logger.info(f"_ensure_model: no model file at {model_path}")
            return
        # guarded imports
        import torch
        from torchvision import models
        import torch.nn as nn

        data = torch.load(str(model_path), map_location='cpu')
        classes = data.get('classes')
        if not classes or 'model_state' not in data:
            logger.warning(f"_ensure_model: model file {model_path} missing required keys")
            return
        model = models.mobilenet_v2(pretrained=False)
        model.classifier[1] = nn.Linear(model.last_channel, len(classes))
        model.load_state_dict(data['model_state'])
        model.eval()
        _MODEL = model
        _MODEL_CLASSES = classes
        logger.info(f"_ensure_model: loaded model from {model_path} with {len(classes)} classes")
    except Exception as e:
        logger.info(f"_ensure_model: could not load model ({e}); continuing without torch-model")
        _MODEL = None
        _MODEL_CLASSES = None


@app.get('/recommend/diseases')
def recommend_diseases():
    data = _load_json_safe(RECS_FILE)
    return {'diseases': sorted(list(data.keys()))}


@app.post('/recommend')
def recommend(payload: dict):
    disease_raw = (payload.get('disease') or '').strip().lower()
    have = payload.get('have') or []
    have = [h.strip().lower() for h in have if h]

    data = _load_json_safe(RECS_FILE)
    syn = _load_json_safe(SYN_FILE)

    disease_key: Optional[str] = None
    if not disease_raw:
        disease_key = 'general' if 'general' in data else (next(iter(data.keys())) if data else None)

    if not disease_key and disease_raw in data:
        disease_key = disease_raw

    if not disease_key:
        for k, vals in syn.items():
            if any(disease_raw == v.lower() for v in vals):
                disease_key = k
                break

    if not disease_key and data:
        candidates = list(data.keys()) + [v for vals in syn.values() for v in vals]
        match = difflib.get_close_matches(disease_raw, candidates, n=1, cutoff=0.6)
        if match:
            m = match[0]
            if m in data:
                disease_key = m
            else:
                for k, vals in syn.items():
                    if m in vals:
                        disease_key = k
                        break

    if not disease_key:
        disease_key = 'general' if 'general' in data else (next(iter(data.keys())) if data else None)

    if not disease_key:
        return {'recommendations': [], 'disease': None}

    candidates = data.get(disease_key, [])
    filtered = [c for c in candidates if c.get('class', '').strip().lower() not in have]

    if not filtered:
        return {'recommendations': [], 'message': 'No new recommendations — you already have the suggested items or none match.', 'disease': disease_key}

    out = []
    for item in filtered[:3]:
        cls = item.get('class')
        sample_file = None
        if cls:
            class_dir = DATA_DIR / cls
            if class_dir.exists() and class_dir.is_dir():
                files = [p.name for p in sorted(class_dir.iterdir()) if p.is_file()]
                if files:
                    sample_file = files[0]
        itm = dict(item)
        if sample_file:
            itm['sample'] = sample_file
        out.append(itm)
    return {'recommendations': out, 'disease': disease_key}


@app.get('/vision/health')
def vision_health():
    # report whether the torch model could be loaded (lazy)
    try:
        _ensure_model()
    except Exception:
        pass
    return {'ok': True, 'model_loaded': _MODEL is not None}


@app.get('/vision/classes')
def vision_classes():
    return {'classes': _get_available_classes()}


@app.get('/vision/samples')
def vision_samples(class_name: str = Query(..., alias='cls'), n: int = Query(6, alias='n')):
    cls_dir = DATA_DIR / class_name
    if not cls_dir.exists() or not cls_dir.is_dir():
        return {'samples': []}
    files = [p.name for p in sorted(cls_dir.iterdir()) if p.is_file()]
    return {'samples': files[:n]}


@app.get('/explore/{name}')
def explore_data(name: str):
    """Return per-fruit JSON stored under data/explore/<name>.json if available."""
    p = PROJECT_ROOT / 'data' / 'explore' / f"{name}.json"
    if not p.exists() or not p.is_file():
        # also try lowercased filename
        p2 = PROJECT_ROOT / 'data' / 'explore' / f"{name.lower()}.json"
        if p2.exists() and p2.is_file():
            p = p2
        else:
            raise HTTPException(status_code=404, detail='not found')
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.info(f"explore_data: failed to read {p}: {e}")
        raise HTTPException(status_code=500, detail='failed to read data')


@app.get('/explore')
def explore_list():
    """Return a list of available fruit JSON files under data/explore for debugging and discovery."""
    d = PROJECT_ROOT / 'data' / 'explore'
    if not d.exists() or not d.is_dir():
        return {'available': []}
    files = [p.name for p in sorted(d.iterdir()) if p.is_file() and p.suffix.lower() == '.json']
    # also return names without extension
    names = [p[:-5] if p.lower().endswith('.json') else p for p in files]
    return {'available': names}


@app.get('/vision/image')
def vision_image(class_name: str = Query(..., alias='cls'), filename: str = Query(..., alias='file')):
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail='invalid filename')
    fpath = DATA_DIR / class_name / filename
    if not fpath.exists() or not fpath.is_file():
        raise HTTPException(status_code=404, detail='file not found')
    return FileResponse(str(fpath))


@app.post('/vision/predict')
async def predict_stub(file: Optional[UploadFile] = File(None), image: Optional[UploadFile] = File(None)):
    # Accept either 'file' or 'image' as the multipart form field for compatibility
    upload = file or image
    if not upload:
        return JSONResponse({'error': 'no file uploaded; expected form field named "file"'}, status_code=422)

    # save upload to a temp path
    try:
        tmp_dir = FILE_DIR / 'tmp'
        tmp_dir.mkdir(exist_ok=True)
        tmp_path = tmp_dir / (getattr(upload, 'filename', 'upload.jpg'))
        with open(tmp_path, 'wb') as f:
            f.write(await upload.read())
    except Exception as e:
        logger.info(f"predict_stub: failed to save upload: {e}")
        return JSONResponse({'error': 'failed to save uploaded file'}, status_code=500)

    try:
        # try torch model first (lazy-loaded)
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
                img = Image.open(str(tmp_path)).convert('RGB')
                tensor = transform(img).unsqueeze(0)
                with torch.no_grad():
                    outputs = _MODEL(tensor)
                    probs = torch.softmax(outputs, dim=1).squeeze(0)
                    topk = torch.topk(probs, k=min(3, probs.numel()))
                    preds = []
                    for idx, score in zip(topk.indices.tolist(), topk.values.tolist()):
                        cls_name = _MODEL_CLASSES[idx] if _MODEL_CLASSES and idx < len(_MODEL_CLASSES) else str(idx)
                        preds.append({'class': cls_name, 'score': float(score)})
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
                return JSONResponse({'predictions': preds, 'source': 'torch-model'})
            except Exception as e:
                logger.info(f"predict_stub: torch inference failed: {e}")

        # fallback: try local helper identify_fruit
        try:
            from vision.image_recognition import identify_fruit  # type: ignore
            res = identify_fruit(str(tmp_path))
            preds = []
            if isinstance(res, str):
                preds = [{'class': res, 'score': 0.9}]
            elif isinstance(res, list):
                if res and isinstance(res[0], (list, tuple)):
                    preds = [{'class': r[0], 'score': float(r[1])} for r in res]
                else:
                    preds = [{'class': r, 'score': 0.9} for r in res]
            elif isinstance(res, dict):
                preds = res.get('predictions') or []
            else:
                preds = [{'class': str(res), 'score': 0.9}]
            try:
                tmp_path.unlink()
            except Exception:
                pass
            return JSONResponse({'predictions': preds, 'source': 'local-identify'})
        except Exception as e:
            logger.info(f"predict_stub: identify_fruit helper not available or failed: {e}")

        # fallback to dev mock if enabled
        if _env_flag('BACKEND_FAKE_PREDICT'):
            fname = getattr(upload, 'filename', None) or 'unknown.jpg'
            fake_classes = _get_available_classes() or ['apple', 'banana', 'orange']
            idx = sum(ord(c) for c in fname) % len(fake_classes)
            fake = {
                'predictions': [
                    {'class': fake_classes[idx], 'score': 0.87},
                    {'class': fake_classes[(idx + 1) % len(fake_classes)], 'score': 0.08},
                ],
                'source': 'dev-mock',
            }
            try:
                tmp_path.unlink()
            except Exception:
                pass
            return JSONResponse(fake)

        # nothing available
        try:
            tmp_path.unlink()
        except Exception:
            pass
        return JSONResponse({'error': 'model not available in this environment'}, status_code=501)
    except Exception as e:
        logger.info(f"predict_stub: unexpected error: {e}")
        try:
            tmp_path.unlink()
        except Exception:
            pass
        return JSONResponse({'error': 'internal error during prediction'}, status_code=500)


# --- Chatbot Endpoint ---
# Add chatbot directory to path
sys.path.append(os.path.join(FILE_DIR, 'chatbot'))

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
            logger.info("Chatbot initialized successfully")
        except Exception as e:
            logger.error(f"Chatbot initialization failed: {e}")
            get_response_func = lambda msg: "I'm sorry, I'm having trouble processing your request right now."

# In-memory session storage (for demo; use Redis/DB in production)
chat_sessions = {}

@app.post("/recipes/generate")
def generate_recipe(
    fruits: list = Body(..., embed=True),
    dietary_preferences: Optional[list] = Body(None, embed=True),
    cuisine_type: Optional[str] = Body(None, embed=True),
    meal_type: Optional[str] = Body(None, embed=True)
):
    """Generate a recipe based on selected fruits and preferences."""
    if not fruits:
        raise HTTPException(status_code=400, detail="At least one fruit must be selected")

    # For now, generate a mock recipe. Later integrate with GPT models
    primary_fruit = fruits[0].lower()

    # Mock recipe templates based on fruit type
    recipe_templates = {
        "apple": {
            "title": "Fresh Apple Cinnamon Oatmeal",
            "ingredients": [
                "2 cups rolled oats",
                "2 cups milk (or almond milk)",
                "2 apples, diced",
                "1 tsp cinnamon",
                "2 tbsp honey",
                "1/4 cup chopped walnuts",
                "Pinch of salt"
            ],
            "instructions": [
                "In a saucepan, bring milk to a gentle boil",
                "Add oats and reduce heat to simmer",
                "Cook for 5 minutes, stirring occasionally",
                "Add diced apples, cinnamon, and honey",
                "Continue cooking for another 3-4 minutes until apples are tender",
                "Serve topped with walnuts and a drizzle of honey"
            ],
            "nutrition": {"calories": 320, "protein": 10, "carbs": 55, "fat": 8},
            "prep_time": "15 minutes",
            "servings": 2
        },
        "banana": {
            "title": "Banana Protein Smoothie Bowl",
            "ingredients": [
                "2 ripe bananas",
                "1 cup Greek yogurt",
                "1/2 cup almond milk",
                "2 tbsp peanut butter",
                "1 tbsp chia seeds",
                "1/2 cup mixed berries",
                "2 tbsp granola"
            ],
            "instructions": [
                "Add bananas, yogurt, almond milk, and peanut butter to a blender",
                "Blend until smooth and creamy",
                "Pour into a bowl",
                "Top with mixed berries, chia seeds, and granola",
                "Serve immediately for best texture"
            ],
            "nutrition": {"calories": 380, "protein": 18, "carbs": 45, "fat": 12},
            "prep_time": "10 minutes",
            "servings": 1
        },
        "berry": {
            "title": "Mixed Berry Antioxidant Salad",
            "ingredients": [
                "2 cups mixed berries (strawberries, blueberries, raspberries)",
                "2 cups mixed greens",
                "1/4 cup feta cheese",
                "1/4 cup walnuts",
                "2 tbsp balsamic vinaigrette",
                "1 tbsp honey",
                "Fresh mint leaves"
            ],
            "instructions": [
                "Wash and prepare all berries",
                "In a large bowl, combine mixed greens and berries",
                "Crumble feta cheese over the salad",
                "Add walnuts and torn mint leaves",
                "Drizzle with balsamic vinaigrette and honey",
                "Toss gently and serve immediately"
            ],
            "nutrition": {"calories": 280, "protein": 8, "carbs": 35, "fat": 14},
            "prep_time": "15 minutes",
            "servings": 2
        }
    }

    # Default recipe if fruit not in templates
    default_recipe = {
        "title": f"Fresh {primary_fruit.title()} Delight",
        "ingredients": [
            f"2 cups fresh {primary_fruit}s",
            "1 cup Greek yogurt",
            "2 tbsp honey",
            "1 tsp vanilla extract",
            "1/2 cup granola",
            "Fresh herbs for garnish"
        ],
        "instructions": [
            f"Prepare the {primary_fruit}s by washing and cutting into pieces",
            "In a bowl, mix yogurt, honey, and vanilla",
            f"Gently fold in the prepared {primary_fruit}s",
            "Divide into serving bowls",
            "Top with granola and fresh herbs",
            "Serve chilled or at room temperature"
        ],
        "nutrition": {"calories": 280, "protein": 12, "carbs": 45, "fat": 8},
        "prep_time": "15 minutes",
        "servings": 2
    }

    # Get recipe template
    recipe = recipe_templates.get(primary_fruit, default_recipe)

    # Apply dietary preferences (basic filtering)
    if dietary_preferences:
        if "Vegan" in dietary_preferences:
            recipe["ingredients"] = [ing.replace("Greek yogurt", "coconut yogurt").replace("feta cheese", "vegan feta") for ing in recipe["ingredients"]]
        if "Gluten-Free" in dietary_preferences:
            recipe["ingredients"] = [ing for ing in recipe["ingredients"] if "oats" not in ing.lower()]

    # Apply meal type adjustments
    if meal_type:
        if meal_type.lower() == "breakfast":
            recipe["title"] = f"Breakfast {recipe['title']}"
        elif meal_type.lower() == "dessert":
            recipe["title"] = f"{recipe['title']} Dessert"

    return recipe

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
        logger.error(f"Chatbot error: {e}")
        bot_response = "I'm sorry, I'm having trouble processing your request right now."

    # Update session history
    chat_sessions[session_id]["history"].append({"user": message, "bot": bot_response})

    return {"response": bot_response, "session_id": session_id}
