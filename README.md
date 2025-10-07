
# Fruitopia AI

Fruitopia AI is an intelligent fruit recommendation system that uses machine learning and AI to suggest the best fruits for users based on their health conditions, preferences, and available inventory. The system features disease-based recommendations, personalized suggestions, natural language input, a conversational chatbot, and fruit image recognition.


## Features & AI Methods
- Disease-based fruit recommendations (Machine Learning)
- Personalized suggestions using user profile (ML/Recommendation Systems)
- Natural Language Processing (NLP) for user input and symptom analysis
- Conversational AI chatbot for interactive experience
- Fruit image recognition (Computer Vision/Deep Learning)

**AI Technologies Used:**
- Machine Learning (scikit-learn, TensorFlow, or PyTorch)
- Natural Language Processing (spaCy, NLTK, or Hugging Face Transformers)
- Computer Vision/Image Recognition (TensorFlow, PyTorch, OpenCV)
- Conversational AI (custom chatbot or integration with frameworks like Rasa)

## Tech Stack
- **Frontend:** Angular
- **Backend:** FastAPI (Python)
- **Machine Learning:** Python (scikit-learn, TensorFlow, or PyTorch as needed)

## Frontend details
- Built with Angular standalone components and Angular Material for UI (toolbar, icons, form-field, input, buttons, tooltips).
- Recent UI improvements: compact/sticky glassy header with integrated search, compact fruit cards, responsive grid, and a floating chatbot button.

## Getting Started
### 1. Clone the repository
```sh
git clone https://github.com/Sanjaya-Samudra/Fruitopia.git
cd Fruitopia
```

### 2. Backend Setup (FastAPI)
- Install Python dependencies:
   ```sh
   pip install fastapi uvicorn
   ```
- Run the backend:
   ```sh
   uvicorn backend.app:app --reload
   ```

### 3. Frontend Setup (Angular)
- Install Node.js and Angular CLI if not already installed.
- Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
- Install dependencies:
   ```sh
   npm install
   ```
- Run the Angular app:
   ```sh
   ng serve --open
   ```

Notes:
- The frontend uses Angular Material modules (MatToolbarModule, MatIconModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatTooltipModule). If you add components that require other Material modules, import them in the relevant standalone component (e.g., `app.component.ts`).

### Quick UI notes
- Header: search is integrated into the sticky toolbar. Use the search input to filter results (client-side filtering can be enabled).
- Chatbot: floating button at bottom-right opens the chatbot prompt (or a slide-up panel if implemented).


## Contributing
We welcome contributions! To contribute:
1. **Fork the repository** on GitHub
2. **Create a new branch** for your feature or bugfix:
    ```sh
    git checkout -b feature/your-feature-name
    ```
3. **Commit your changes** and push to your fork:
    ```sh
    git add .
    git commit -m "Add your feature"
    git push origin feature/your-feature-name
    ```
4. **Open a Pull Request** to the main repository.


## License
MIT

## Contact
For questions or support, open an issue or contact the maintainer.
