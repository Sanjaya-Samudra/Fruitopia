
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

## 🚀 **Updated Setup Guide (2025)**

### **Prerequisites**
- **Python 3.12+** (recommended for best compatibility)
- **Node.js 18+** and npm
- **Git**
- **PowerShell** (Windows) or **Terminal** (macOS/Linux)

### **📦 Current Dependencies**

#### **Backend Dependencies** (`backend/requirements.txt`)
```
fastapi>=0.118.0
uvicorn>=0.37.0
requests>=2.32.5
transformers>=4.57.0
torch>=2.8.0
sentence-transformers>=5.1.1
scikit-learn>=1.7.2
pandas>=2.3.3
numpy>=2.2.6
nltk>=3.9.2
pydantic>=2.12.0
```

#### **Frontend Dependencies** (`frontend/package.json`)
```
@angular/core: ^19.2.0
@angular/material: ^19.2.19
@angular/cdk: ^19.2.19
@asymmetrik/ngx-leaflet: ^17.0.0
leaflet: ^1.9.4
rxjs: ~7.8.0
```

### **🛠️ Complete Setup Instructions**

#### **Step 1: Clone and Navigate**
```powershell
git clone <your-repo-url> Fruitopia
cd Fruitopia
```

#### **Step 2: Backend Setup**
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install all backend dependencies
pip install -r backend/requirements.txt

# Download NLTK data (required for chatbot)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

#### **Step 3: Frontend Setup**
```powershell
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to root directory
cd ..
```

#### **Step 4: Start the Services**

**Terminal 1 - Backend Server:**
```powershell
# Activate virtual environment (if not already activated)
.\.venv\Scripts\Activate.ps1

# Start FastAPI server
uvicorn backend.vision_api:app --host 127.0.0.1 --port 8000 --reload
```
Backend will be available at: `http://127.0.0.1:8000`
API Documentation: `http://127.0.0.1:8000/docs`

**Terminal 2 - Frontend Server:**
```powershell
cd frontend
ng serve --configuration development --port 4200 --proxy-config proxy.conf.json
```
Frontend will be available at: `http://localhost:4200`

### **🤖 Enhanced AI Chatbot Features**

The Fruitopia chatbot is a **custom-built, transformer-based conversational AI** that uses modern NLP techniques instead of traditional rule-based frameworks like Rasa.

#### **Chatbot Architecture:**
- **Framework**: Custom Python implementation (not Rasa, Dialogflow, or similar)
- **NLP Engine**: Sentence Transformers (`all-MiniLM-L6-v2`) for semantic understanding
- **Intent Classification**: Cosine similarity-based intent detection (175+ training examples)
- **Entity Extraction**: Rule-based + fuzzy matching for fruits, diseases, and contexts
- **Response Generation**: Template-based with randomization for natural conversations
- **Training Data**: 17 intents covering diverse fruit-related topics

#### **Comparison with Traditional Chatbots:**
| Feature | Fruitopia Chatbot | Traditional Frameworks (Rasa/Dialogflow) |
|---------|------------------|-----------------------------------------|
| **Setup Complexity** | Low (pure Python) | High (framework-specific training) |
| **Python 3.12+ Compatibility** | ✅ Full support | ❌ Many compatibility issues |
| **Customization** | ✅ Fully customizable | ⚠️ Limited by framework constraints |
| **Dependencies** | Lightweight (transformers + sklearn) | Heavy (framework + dependencies) |
| **Training Data** | JSON-based (human readable) | YAML/domain files (complex) |
| **Deployment** | Simple FastAPI integration | Framework-specific deployment |
| **Maintenance** | Easy (pure Python) | Complex (framework updates) |

#### **Why Custom Implementation:**
- **Modern AI**: Uses state-of-the-art sentence transformers instead of older NLP techniques
- **Python 3.12+ Ready**: No compatibility issues with latest Python versions
- **Lightweight**: Minimal dependencies, fast startup
- **Domain-Specific**: Optimized for fruit/nutrition conversations
- **Easy Maintenance**: Pure Python code, no framework lock-in
- **Cost-Effective**: No external API costs or framework licenses

The Fruitopia chatbot now supports **17 different conversation intents**:

#### **Core Capabilities:**
- **Health Recommendations**: Disease-specific fruit suggestions (diabetes, hypertension, etc.)
- **Fruit Information**: Detailed nutritional data and benefits
- **Quantity Guidance**: Serving sizes and daily recommendations
- **Seasonal Info**: When fruits are in season and best to eat
- **Recipes**: Cooking ideas and meal suggestions
- **Allergy Warnings**: Safety information for fruit allergies
- **Storage Tips**: How to store fruits for freshness
- **Fun Facts**: Interesting trivia about fruits
- **Comparisons**: Nutritional comparisons between fruits
- **Meal Planning**: Breakfast, lunch, dinner ideas

#### **Example Conversations:**
```
👤 "I have diabetes, what fruits should I eat?"
🤖 "For diabetes, I recommend these fruits: apples, bananas, oranges, berries, citrus fruits"

👤 "How much apple should I eat daily?"
🤖 "For optimal health benefits, aim for 1 medium piece or 1 cup of apples per day"

👤 "Do you have recipes with mango?"
🤖 "Here are some cooking ideas with mangos: mangos smoothies, mangos salad, baked mangos, mangos desserts"

👤 "I'm allergic to strawberries"
🤖 "Caution: strawberries contains oral allergy syndrome which some people are sensitive to"
```

### **🔧 Development Environment**

#### **Virtual Environment Management**
```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Deactivate when done
deactivate
```

#### **Testing the Chatbot**
```powershell
# Quick chatbot test
python -c "
from backend.chatbot.custom_chatbot import initialize_chatbot, get_response
initialize_chatbot()
print('Bot:', get_response('Hello!'))
print('Bot:', get_response('I have diabetes'))
"
```

#### **API Endpoints**
- `POST /chatbot/message` - Chatbot conversations
- `GET /fruits` - Fruit database
- `POST /recommend` - Health-based recommendations
- `POST /nlp/extract` - Disease/symptom extraction
- `POST /vision/identify` - Fruit image recognition

### **🐛 Troubleshooting**

#### **Common Issues:**

**1. "Module not found" errors:**
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r backend/requirements.txt
```

**2. "NLTK data not found":**
```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

**3. "Port already in use":**
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
# Use the PID from output
taskkill /PID <PID> /F
```

**4. Frontend proxy issues:**
- Ensure backend is running on port 8000
- Check `frontend/proxy.conf.json` configuration
- Restart Angular dev server after backend changes

#### **Performance Notes:**
- First chatbot initialization may take 10-30 seconds (downloads AI models)
- Subsequent requests are fast (<1 second)
- Virtual environment keeps dependencies isolated and clean

### **📝 Contributing Guidelines**

#### **For New Developers:**
1. Follow the setup guide above
2. Test both backend and frontend locally
3. Use the chatbot to understand current capabilities
4. Check API documentation at `/docs` endpoint
5. Keep virtual environment activated during development

#### **Code Style:**
- Backend: Follow PEP 8 Python standards
- Frontend: Follow Angular style guide
- Commit messages: Use conventional commits format

#### **Adding New Features:**
- Update training data in `backend/chatbot/data/training_data.json`
- Add new intents to `custom_chatbot.py`
- Test thoroughly with diverse inputs
- Update this README if new dependencies are added

---

**🎉 Ready to contribute! The Fruitopia AI system is now fully set up with an advanced conversational chatbot capable of handling diverse fruit-related queries.**
