import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import routers
from app.routes import planner, scheduler, study_plan, teacher, practice, revision, exam

load_dotenv()

# Configure API key
gemini_api_key = os.getenv("GEMINI_API_KEY") or "YOUR_PLACEHOLDER_KEY"
genai.configure(api_key=gemini_api_key)


model = genai.GenerativeModel('gemini-pro')

app = FastAPI(
    title="AI Study Assistant API",
    description="Backend API for the AI Study Assistant, powered by Google Gemini Pro.",
    version="0.0.1",
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "null",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Study Assistant API!"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}

# Include routers
app.include_router(planner.router, prefix="/study_plan", tags=["Planner"])
app.include_router(scheduler.router, prefix="/scheduler", tags=["Scheduler"])
# app.include_router(study_plan.router, prefix="/study_plan_old", tags=["Study Plan Old"]) # Commenting out old one if needed
app.include_router(teacher.router, prefix="/teacher", tags=["Teacher Mode"])
app.include_router(practice.router, prefix="/practice", tags=["Practice Mode"])
app.include_router(revision.router, prefix="/revision", tags=["Revision Mode"])
app.include_router(exam.router, prefix="/exam", tags=["Exam Strategy"])

