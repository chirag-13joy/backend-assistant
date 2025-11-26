from fastapi import APIRouter
from app.logic.scheduler import generate_study_plan, build_topics_from_payload, study_plan_to_dict
from app.schemas import StudyPlanRequest, StudyPlanResponse
from datetime import date

router = APIRouter()

@router.post("/generate_study_plan", response_model=StudyPlanResponse)
def generate_plan(request: StudyPlanRequest):
    topics = build_topics_from_payload(request.topics)
    plan = generate_study_plan(
        topics=topics,
        start_date=request.start_date,
        exam_date=request.exam_date,
        hours_per_day=request.hours_per_day,
    )
    return study_plan_to_dict(plan)
