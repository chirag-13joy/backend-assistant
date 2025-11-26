from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import date

# Input JSONs
class StudyTopicInput(BaseModel):
    subject_name: str
    topic_name: str
    difficulty: Literal["easy", "medium", "hard"]
    weight: Literal["low", "medium", "high"]
    weakness: Literal["strong", "moderate", "weak"]
    progress: float = Field(..., ge=0, le=1) # Progress between 0.0 and 1.0
    base_hours: float

class PlannerRequest(BaseModel):
    topics: List[StudyTopicInput]
    start_date: date
    exam_date: date
    hours_per_day: float = Field(..., gt=0) # Must be greater than 0

class StudyPlanRequest(PlannerRequest):
    pass


class TeacherRequest(BaseModel):
    user_id: str
    topic: str
    context: str # e.g., text from a textbook or an article
    explanation_style: Literal["simple", "detailed", "analogy"]

class PracticeRequest(BaseModel):
    user_id: str
    topic: str
    num_questions: int
    difficulty: Literal["easy", "medium", "hard"]

# Output JSONs
class StudyPlannerModule(BaseModel):
    module_title: str
    description: str
    estimated_time_minutes: float
    resources: List[str]

class StudyPlannerResponse(BaseModel):
    plan_id: str
    user_id: str
    title: str
    estimated_duration_hours: float
    modules: List[StudyPlannerModule]

class TeacherResponse(BaseModel):
    user_id: str
    topic: str
    explanation: str
    keywords: List[str]

class PracticeResponse(BaseModel):
    user_id: str
    question_id: str
    question_text: str
    options: List[str]
    correct_answer: str
    explanation: str


# Scheduler-related output models
class Task(BaseModel):
    topic_name: str
    subject_name: str
    task_type: str
    duration_hours: float
    priority_score: float

class PlanDay(BaseModel):
    date: date
    tasks: List[Task]
    total_hours: float

class StudyPlanResponse(BaseModel):
    days: List[PlanDay]
    start_date: date
    exam_date: date
    hours_per_day: float
    status: str
