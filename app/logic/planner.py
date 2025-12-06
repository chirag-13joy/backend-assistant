import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from teacher.Scheduler import build_topics_from_payload, generate_study_plan, study_plan_to_dict
from schemas import PlannerRequest

def create_study_plan(request: PlannerRequest):
    """
    Generate a study plan based on a list of topics and a date range.
    """
    # The request body is a PlannerRequest, which has a 'topics' field
    # that is a list of Pydantic models. We need to convert them to dicts
    # for build_topics_from_payload.
    topics_payload = [topic.model_dump() for topic in request.topics]

    topics = build_topics_from_payload(topics_payload)

    study_plan = generate_study_plan(
        topics=topics,
        start_date=request.start_date,
        exam_date=request.exam_date,
        hours_per_day=request.hours_per_day
    )

    # Convert the StudyPlan object to a dictionary for the response
    return study_plan_to_dict(study_plan)
