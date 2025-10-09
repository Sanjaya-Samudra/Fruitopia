# Fruitopia — AI assets and provenance

This file documents the image dataset you provided and the planned AI steps to reproduce preprocessing, training, and inference.

1) Dataset provenance
- Local image dataset: `data/FruitImageDataset` — provided by the user (contains 826 images across ~30 classes). The folder structure is expected to be one folder per class (e.g., `apple`, `banana`, ...).
- External data (to be used later): USDA FoodData Central — large dataset; user previously downloaded a full dump and removed it because it contained mixed data. We'll instead fetch smaller, focused CSVs or use curated nutrition datasets if needed.
- NLP/chatbot: we will use open-source datasets such as the Cornell Movie Dialogs (for conversational data), FAQ-like datasets, or build a retrieval dataset from public nutritional articles. Exact sources will be recorded when fetched.

2) Local scripts and API
- `ml/inspect_dataset.py` — scans `data/FruitImageDataset` and writes `ml/metadata.json` with class counts and samples.
- `ml/requirements.txt` — Python packages suggested for ML training and inference.
- `backend/vision_api.py` — FastAPI stub for image prediction; will be extended to load the trained model and return predictions.

3) Repro steps (local)

Prerequisites: Python 3.8+ and a virtual environment.

Install dependencies:
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r ml/requirements.txt
```

Inspect dataset and generate metadata:
```powershell
python ml\inspect_dataset.py
type ml\metadata.json
```

Run API (stub):
```powershell
uvicorn backend.vision_api:app --reload
```

Create deterministic splits (train/val/test):
```powershell
python ml\preprocess_split.py
```

Train a quick transfer-learning model (MobileNetV2):
```powershell
python ml\train.py
```

Notes on provenance:
- The image dataset in `data/FruitImageDataset` was provided by the user and inspected with `ml/inspect_dataset.py`. The script wrote class counts and samples to `ml/metadata.json` (snapshot included in the repo). Keep this file as an audit trail.
- If you later fetch external nutrition or NLP datasets (USDA, etc.), save the original downloaded files and record their SHA256 sums and URLs here.

4) Next steps
- Implement `ml/preprocess_split.py` to create deterministic train/val/test splits.
- Implement `ml/train.py` to train a transfer-learning model (MobileNetV2/ResNet18) and save to `ml/models/fruit_classifier.pt`.
- Update `backend/vision_api.py` to load the trained model and perform real inference.
- Add frontend integration and image upload UI in Angular to call `/vision/predict`.

5) Recording provenance
- When fetching external datasets (USDA or others), the exact URLs and download timestamps will be recorded here with SHA256 checksums of downloaded files.
