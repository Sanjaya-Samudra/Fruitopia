# Simple chatbot stub for Fruitopia
from typing import List

def get_response(user_message: str) -> str:
    # Basic rule-based responses
    if 'recommend' in user_message:
        return 'Sure! Please tell me your disease or symptoms.'
    elif 'hello' in user_message or 'hi' in user_message:
        return 'Hello! I am your Fruitopia assistant.'
    else:
        return 'I can help you find healthy fruits. Ask me for recommendations!'

# Example usage
if __name__ == "__main__":
    print(get_response('Can you recommend something for diabetes?'))
