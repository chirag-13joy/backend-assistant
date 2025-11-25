import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Import routers
from app.routes import planner # Import the new planner router

load_dotenv()

# Configure API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-pro')

app = FastAPI(
    title="AI Study Assistant API",
    description="Backend API for the AI Study Assistant, powered by Google Gemini Pro.",
    version="0.0.1",
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Study Assistant API!"}

# Include the new planner router
app.include_router(planner.router, prefix="/planner", tags=["Planner"])

# Placeholder for other routers like /teacher, /practice etc.
# app.include_router(teacher.router, prefix="/teacher", tags=["Teacher Mode"])
# app.include_router(practice.router, prefix="/practice", tags=["Practice Mode"])

