from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import date

# Assuming the logic is in the app directory, and we can import it.
# We might need to adjust the Python path for this to work.
import sys
sys.path.append('/mnt/c/Users/Lenovo/ai_study_assistant_backend')
from app.logic.scheduler import build_topics_from_payload, generate_study_plan, study_plan_to_dict
from app.models.study_plan import StudyTopic, StudyPlan


router = APIRouter()

class PlannerRequest(BaseModel):
    topics: List[str]
    start_date: date
    exam_date: date
    hours_per_day: float

@router.post("/generate-plan")
async def generate_plan(request: PlannerRequest):
    """
    Generates a study plan based on a list of topics, a start date, an exam date, and the number of hours per day.
    """
    try:
        # 1. Build topics from the payload
        topic_objects = build_topics_from_payload([{"topic_name": name, "subject_name": "General", "difficulty": "medium", "weight": "medium", "weakness": "moderate"} for name in request.topics])

        # 2. Generate the study plan
        study_plan = generate_study_plan(
            topics=topic_objects,
            start_date=request.start_date,
            exam_date=request.exam_date,
            hours_per_day=request.hours_per_day
        )

        # 3. Convert the StudyPlan to a JSON-serializable dictionary
        plan_dict = study_plan_to_dict(study_plan)

        return plan_dict

    except Exception as e:
        return {"error": True, "message": str(e)}
