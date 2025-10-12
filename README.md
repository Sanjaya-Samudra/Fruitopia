
# Fruitopia AI

Fruitopia AI is an intelligent fruit recommendation system that uses machine learning and AI to suggest the best fruits for users based on their health conditions, preferences, and available inventory. The system features disease-based recommendations, personalized suggestions, natural language input, a conversational chatbot, and fruit image recognition.

## Features & AI Methods
- Disease-based fruit recommendations (Machine Learning)
- Personalized suggestions using user profile (ML/Recommendation Systems)
- Natural Language Processing (NLP) for user input and symptom analysis
- Conversational AI chatbot for interactive experience
- Fruit image recognition (Computer Vision/Deep Learning)
- **Comprehensive Fruit Encyclopedia** with detailed nutritional data, cultivation info, and interactive maps
- **Interactive Geolocation Maps** showing fruit origins and cultivation regions

**AI Technologies Used:**
- Machine Learning (scikit-learn, TensorFlow, or PyTorch)
- Natural Language Processing (spaCy, NLTK, or Hugging Face Transformers)
- Computer Vision/Image Recognition (TensorFlow, PyTorch, OpenCV)
- Conversational AI (custom chatbot or integration with frameworks like Rasa)

## Frontend Features

### Explore Component
The `/explore/[fruit-name]` route provides a comprehensive fruit encyclopedia with:

- **6 Organized Tabs**: Overview, Nutrition & Health, Culinary & Uses, Science & Botany, Cultivation, and Facts & More
- **Interactive Maps**: Leaflet-powered maps showing fruit origins and cultivation regions
- **Nutritional Data**: Detailed vitamins, minerals, and macronutrient information with visual charts
- **Modern UI**: Card-based design with gradients, animations, and responsive layouts
- **Image Gallery**: Fruit photos with lightbox viewing
- **Comprehensive Data**: Botanical information, health benefits, culinary uses, and more

### Recommendation System
- Disease-based fruit recommendations
- Personalized suggestions
- Natural language symptom analysis

## Tech Stack
- **Frontend:** Angular with Leaflet for interactive maps
- **Backend:** FastAPI (Python)
- **Machine Learning:** Python (scikit-learn, TensorFlow, or PyTorch as needed)
# Fruitopia (Angular + FastAPI)

This README is a step-by-step guide to get Fruitopia running locally on Windows (PowerShell). It is written so a newbie can follow copy-paste commands.

Project layout (important files)
--------------------------------
- `frontend/` — Angular app (dev server runs on http://localhost:4200)
- `backend/` — FastAPI app (`backend/vision_api.py`)
- `backend/ml/` — recommender JSON files, optional models
- `data/FruitImageDataset/` — dataset (one folder per fruit class)

Prerequisites
-------------
- Node.js (16+), npm (or pnpm)
- Python 3.10+
- Git
- PowerShell (Windows)

1) Clone the repo
------------------
Open PowerShell:

```powershell
git clone <your-repo-url> Fruitopia
cd Fruitopia
```

2) Backend setup (FastAPI)
--------------------------
Create and activate a Python virtual environment, then install required packages.

```powershell
# from repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install fastapi uvicorn
# Optional (only if you plan to run vision/predict): install torch/torchvision appropriate for your hardware
# Example CPU-only (check https://pytorch.org for current instructions):
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

Creating and using the recommended `.venv` (expanded)
---------------------------------------------------
We recommend a repository-local virtual environment named `.venv`. This keeps dependencies scoped to the project and avoids polluting the global Python environment.

Windows (PowerShell) — copy/paste:

```powershell
# create the venv
python -m venv .venv

# on first use you may need to allow script execution (one-time; admin may be required):
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# activate the venv (PowerShell)
.\.venv\Scripts\Activate.ps1

# install core dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt
```

macOS / Linux (bash / zsh):

```bash
# create the venv
python3 -m venv .venv

# activate
source .venv/bin/activate

# install
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

Freezing dependencies (create a reproducible list):

```powershell
# from project root with .venv activated
pip freeze > backend/requirements.lock
```

Notes on activation errors on Windows
------------------------------------
- If PowerShell refuses to run the activation script, run as Administrator or set the ExecutionPolicy for your user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- Alternatively use cmd.exe activation (less common):

```cmd
.venv\Scripts\activate.bat
```

What to do if you accidentally committed `.venv` or big files
-----------------------------------------------------------
- If `.venv` was accidentally committed, remove it from git tracking (keeps local copy):

```powershell
git rm -r --cached .venv
git commit -m "chore: remove .venv from repo"
git push origin main
```

- If you need to remove the files from history use `git filter-repo` (recommended) or `git filter-branch` (legacy). Coordinate with your team before rewriting history.


Important notes about `.venv` and git
------------------------------------
- We recommend using a local virtual environment named `.venv` in the repository root. This keeps project dependencies isolated and is ignored by the provided `.gitignore`.
- Make sure you do not commit the `.venv` folder. If you accidentally committed it, follow the cleanup steps below.

How to remove accidentally committed `.venv` or large files
---------------------------------------------------------
If you accidentally committed large files (for example a `.venv` or model artifacts), remove them from the repository and from git history as follows:

1. Stop the dev servers and ensure your working tree is clean.

2. Remove the files from git tracking (this removes them from future commits but keeps them locally):

```powershell
git rm -r --cached .venv
git commit -m "chore: remove .venv from repository"
git push origin main
```

3. (Optional, more aggressive) If you need to purge large files from repository history use the `git filter-repo` tool (recommended) or `git filter-branch` (legacy). Example with `git filter-repo`:

```powershell
# Install git-filter-repo (follow instructions at https://github.com/newren/git-filter-repo)
# Example removal command:
git filter-repo --path .venv --invert-paths
# After rewriting history, force-push the cleaned branch (be careful: this rewrites history):
git push --force origin main
```

Note: Rewriting history is destructive for shared repositories. Coordinate with collaborators before doing a history rewrite.

Run the backend:

```powershell
uvicorn backend.vision_api:app --host 127.0.0.1 --port 8000 --reload
```

Quick smoke checks (separate PowerShell window):

```powershell
Invoke-WebRequest -Uri 'http://127.0.0.1:8000/recommend/diseases' -UseBasicParsing
Invoke-WebRequest -Uri 'http://127.0.0.1:8000/vision/classes' -UseBasicParsing
```

3) Frontend setup (Angular)
---------------------------
Install node deps and run the dev server. The dev server uses `frontend/proxy.conf.json` to forward API calls to the backend.

```powershell
cd frontend
npm install
ng serve --configuration development --port 4200 --proxy-config proxy.conf.json
```

Open http://localhost:4200/ and go to the Recommend page at `/recommend`.

4) Proxy notes
--------------
The frontend makes relative API calls (e.g. `/recommend/diseases` and `/vision/classes`). The dev proxy forwards `/vision` and `/recommend` to the backend at `http://127.0.0.1:8000`.
If you change the backend host or port, update `frontend/proxy.conf.json`.

5) Adding a model later (optional)
----------------------------------
If you add a PyTorch model, place it under `backend/ml/models/` and load it lazily inside the request handler in `backend/vision_api.py` so the server starts without heavy dependencies.

6) Troubleshooting
-------------------
- Backend import-time errors (SyntaxError/IndentationError): inspect `backend/vision_api.py` for bad edits. Avoid importing heavy packages at module import time.
- Dropdown on Recommend page empty: restart Angular dev server (so proxy changes apply) and confirm backend is running. Check browser DevTools Console for errors.
- CORS: the backend allows `http://localhost:4200`. Update the CORS list in `backend/vision_api.py` if needed.

7) Tests and CI (recommended)
-----------------------------
Add `pytest` tests for the backend (`backend/tests/`) and a small Playwright or Cypress e2e test for the frontend. Add a GitHub Actions workflow to run them on PRs.

8) Docker (optional)
--------------------
Consider adding `docker-compose.yml` later to run both services together.

Need me to do more?
--------------------
I can:
- Add a `requirements.txt` and `package.json` scripts for easier start-up.
- Add CI workflow and tests.
- Dockerize the stack.

If you want any of those, tell me which and I will implement next.
