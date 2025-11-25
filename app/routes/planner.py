from fastapi import APIRouter, HTTPException
from app.schemas import PlannerRequest, StudyPlanResponse, StudyTopicInput
from typing import List
from datetime import date, timedelta

router = APIRouter()

# --- Placeholder for Dev 1's Scheduler Logic ---
# This is a mock implementation that we'll replace with Dev 1's code.

def build_topics_from_payload(topics: List[StudyTopicInput]) -> List[StudyTopicInput]:
    """
    Placeholder function to process the topics payload.
    For now, it just returns the topics as is.
    """
    print("Building topics from payload...")
    # In a real scenario, this might convert Pydantic models to a different class
    # or perform some initial validation/filtering.
    return topics

def generate_study_plan(topics: List[StudyTopicInput], start_date: date, exam_date: date, hours_per_day: float) -> StudyPlanResponse:
    """
    Placeholder for Dev 1's core study plan generation logic.
    Creates a simple, dummy study plan based on the inputs.
    """
    print("Generating study plan...")
    
    total_days = (exam_date - start_date).days
    total_study_hours = total_days * hours_per_day
    
    # Create a simple module for each topic provided
    modules = []
    for topic in topics:
        module = {
            "module_title": f"{topic.subject_name}: {topic.topic_name}",
            "description": f"Focus on {topic.topic_name}, a topic with {topic.difficulty} difficulty.",
            "estimated_time_minutes": topic.base_hours * 60,
            "resources": [f"Textbook chapter on {topic.topic_name}", "Online tutorials"]
        }
        modules.append(module)

    # In a real scenario, the scheduler would intelligently allocate these modules
    # across the available days.
    
    return StudyPlanResponse(
        plan_id="dummy_plan_from_scheduler_123",
        user_id="user_placeholder", # Assuming user context might be handled differently
        title="Generated Study Plan",
        estimated_duration_hours=total_study_hours,
        modules=modules
    )
# --- End of Placeholder Logic ---


@router.post("/generate-plan", response_model=StudyPlanResponse)
async def generate_plan_endpoint(request: PlannerRequest):
    """
    API endpoint to generate a new study plan.
    """
    # --- Input Validation ---
    if not request.topics:
        raise HTTPException(status_code=400, detail="No topics provided.")
    
    if request.start_date >= request.exam_date:
        raise HTTPException(status_code=400, detail="Start date must be before exam date.")
    
    if request.hours_per_day <= 0:
        raise HTTPException(status_code=400, detail="Hours per day must be a positive value.")

    # --- Call Dev 1's Logic (using placeholders) ---
    
    # 1. Build topics from the payload
    processed_topics = build_topics_from_payload(request.topics)
    
    # 2. Generate the study plan
    study_plan = generate_study_plan(
        topics=processed_topics,
        start_date=request.start_date,
        exam_date=request.exam_date,
        hours_per_day=request.hours_per_day
    )
    
    # 3. Convert StudyPlan to JSON dict for response (FastAPI handles this automatically)
    return study_plan
