from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Test Backend')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
def read_root():
    return {'message': 'Hello World'}

@app.post('/chatbot/message')
def chatbot_message(message: str):
    return {'response': f'You said: {message}', 'session_id': 'test'}
