import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Configure API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-pro')

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

class SummaryRequest(BaseModel):
    text: str

class ChatRequest(BaseModel):
    message: str
    history: list = [] # To store conversation history

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Study Assistant API!"}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    # Placeholder for AI model integration (e.g., Google Gemini Pro)
    # You will replace this with actual AI API calls.
    ai_response = f"AI's answer to '{request.question}': This is a placeholder response."
    return {"answer": ai_response}

@app.post("/summarize")
async def summarize_text(request: SummaryRequest):
    # Placeholder for AI model integration
    ai_summary = f"AI's summary of '{request.text[:50]}...': This is a placeholder summary."
    return {"summary": ai_summary}

@app.post("/chat")
async def chat_with_assistant(request: ChatRequest):
    # Placeholder for AI model integration with conversation history
    # You would typically feed the history and current message to the AI model
    ai_chat_response = f"AI's response to '{request.message}': This is a placeholder chat response."
    # For now, we'll just return the current message as part of the history for demonstration
    new_history = request.history + [{"user": request.message, "assistant": ai_chat_response}]
    return {"response": ai_chat_response, "history": new_history}

