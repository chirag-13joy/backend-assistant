from fastapi import APIRouter
from app.schemas import TopicsRequest, StudyPlanResponse, TeacherRequest, TeacherResponse, PracticeRequest, PracticeResponse
from typing import List

router = APIRouter()

@router.post("/plan", response_model=StudyPlanResponse)
async def create_study_plan(request: TopicsRequest):
    subjects_in_plan = list(set([topic.subject_name for topic in request.topics]))
    plan_title = f"Study Plan for {', '.join(subjects_in_plan)}"

    dummy_modules = []
    for topic_input in request.topics:
        dummy_modules.append({
            "module_title": f"{topic_input.subject_name}: {topic_input.topic_name}",
            "description": f"Review of {topic_input.topic_name} with difficulty: {topic_input.difficulty} and weakness: {topic_input.weakness}.",
            "estimated_time_minutes": topic_input.base_hours * 60, # Convert hours to minutes
            "resources": [f"Resources for {topic_input.topic_name}", "Additional materials"]
        })

    dummy_plan = StudyPlanResponse(
        plan_id="dummy_plan_id_123",
        user_id=request.user_id,
        title=plan_title,
        estimated_duration_hours=request.duration_hours,
        modules=dummy_modules
    )

@router.post("/explain", response_model=TeacherResponse)
async def get_explanation(request: TeacherRequest):
    # Placeholder for AI model integration for teacher explanations
    dummy_explanation = TeacherResponse(
        user_id=request.user_id,
        topic=request.topic,
        explanation=f"This is a placeholder explanation for '{request.topic}' in a {request.explanation_style} style.",
        keywords=["placeholder", request.topic, request.explanation_style]
    )
    return dummy_explanation

@router.post("/practice", response_model=PracticeResponse)
async def get_practice_question(request: PracticeRequest):
    # Placeholder for AI model integration to generate practice questions
    dummy_question = PracticeResponse(
        user_id=request.user_id,
        question_id="dummy_q_1",
        question_text=f"What is a key concept in '{request.topic}'?",
        options=["Option A", "Option B", "Option C", "Option D"],
        correct_answer="Option A",
        explanation="This is a placeholder explanation for the correct answer."
    )
    return dummy_question
