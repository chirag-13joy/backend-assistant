from fastapi import APIRouter, HTTPException
from app.schemas import StudyPlanRequest, StudyPlanResponse
from app.logic.scheduler import generate_study_plan, build_topics_from_payload, study_plan_to_dict
from datetime import date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate_study_plan", response_model=StudyPlanResponse)
def generate_plan(request: StudyPlanRequest):
    """
    Generates a study plan based on user-provided topics, dates, and study hours.
    """
    try:
        logger.info(f"Received request to generate study plan: {request}")
        
        if not request.topics:
            raise HTTPException(status_code=400, detail="No topics provided.")
        
        # Convert Pydantic models to Topic objects
        topics_data = [topic.model_dump() for topic in request.topics]
        topics = build_topics_from_payload(topics_data)
        logger.info(f"Built {len(topics)} topic objects from payload.")
        
        # Generate the study plan
        plan = generate_study_plan(
            topics=topics,
            start_date=request.start_date,
            exam_date=request.exam_date,
            hours_per_day=request.hours_per_day,
        )
        logger.info("Successfully generated study plan.")
        
        # Convert the plan to a dictionary for the response
        response_data = study_plan_to_dict(plan)
        logger.info("Successfully converted study plan to dictionary.")
        
        return response_data

    except HTTPException as http_exc:
        logger.error(f"HTTP exception occurred: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"An unexpected error occurred during study plan generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
