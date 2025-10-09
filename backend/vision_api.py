"""Clean, minimal Fruitopia backend module.

This file exposes only the endpoints the frontend needs and avoids optional
heavy dependencies so it imports reliably. Once this is stable we can
add guarded model loading separately.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
from typing import Optional
import json
import difflib


FILE_DIR = Path(__file__).resolve().parent  # backend/
PROJECT_ROOT = FILE_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'FruitImageDataset'
RECS_FILE = FILE_DIR / 'ml' / 'disease_recs.json'
SYN_FILE = FILE_DIR / 'ml' / 'disease_synonyms.json'
META_FILE = FILE_DIR / 'ml' / 'metadata.json'

app = FastAPI(title='Fruitopia - clean backend')

# Development CORS: allow Angular dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
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
    return {'ok': True, 'model_loaded': False}


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


@app.get('/vision/image')
def vision_image(class_name: str = Query(..., alias='cls'), filename: str = Query(..., alias='file')):
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail='invalid filename')
    fpath = DATA_DIR / class_name / filename
    if not fpath.exists() or not fpath.is_file():
        raise HTTPException(status_code=404, detail='file not found')
    return FileResponse(str(fpath))


@app.post('/vision/predict')
async def predict_stub(file: UploadFile = File(...)):
    return JSONResponse({'error': 'model not available in this environment'}, status_code=501)
