import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Import routers
from app.routes import planner, scheduler, study_plan # Import the new planner and scheduler router

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
app.include_router(scheduler.router, prefix="/scheduler", tags=["Scheduler"])
app.include_router(study_plan.router, prefix="/study_plan", tags=["Study Plan"])

# Placeholder for other routers like /teacher, /practice etc.
# app.include_router(teacher.router, prefix="/teacher", tags=["Teacher Mode"])
# app.include_router(practice.router, prefix="/practice", tags=["Practice Mode"])

