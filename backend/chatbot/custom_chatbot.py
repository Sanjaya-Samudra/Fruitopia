"""Custom Chatbot Module - Delegates to RAG pipeline."""

import sys, os
from pathlib import Path

FILE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FILE_DIR.parent))
os.chdir(FILE_DIR.parent)

from chatbot.rag_chatbot import initialize, get_response

_initialized = False


def initialize_chatbot():
    global _initialized
    if not _initialized:
        try:
            initialize()
            _initialized = True
            print("Custom chatbot initialized (RAG pipeline)")
        except Exception as e:
            print(f"Custom chatbot init failed: {e}")


def get_response(message: str) -> str:
    if not _initialized:
        initialize_chatbot()
    try:
        from chatbot.rag_chatbot import get_response as rag_response
        return rag_response(message)
    except Exception as e:
        return f"I'm here to help with fruit questions! I'm having a moment to think. Could you rephrase that? ({e})"


if __name__ == "__main__":
    initialize_chatbot()
    print(get_response("Hello, tell me about apples"))
