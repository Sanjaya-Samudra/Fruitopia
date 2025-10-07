# Simple NLP pipeline for extracting disease/symptom from user input
import re
from typing import List

def extract_diseases(text: str) -> List[str]:
    # Example: match common diseases (expand as needed)
    diseases = ['diabetes', 'heart', 'memory', 'immune']
    found = [d for d in diseases if re.search(rf'\b{d}\b', text, re.IGNORECASE)]
    return found

# Example usage
if __name__ == "__main__":
    user_input = "I have diabetes and heart issues."
    print(extract_diseases(user_input))
