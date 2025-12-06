from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import sys
sys.path.append('/mnt/c/Users/Lenovo/ai_study_assistant_backend')

# Now importing from the actual teacher_mode.py
from app.teacher.modes.teacher_mode import teacher_llm_request
from app.logic.scheduler import build_topics_from_payload, Topic, StudyPlan

router = APIRouter()

# In-memory session store - this should be shared, but for now, it's here.
sessions: Dict[str, Dict[str, Any]] = {}

class TeacherRequest(BaseModel):
    action: str
    payload: Dict[str, Any]
    session_state: Dict[str, Any]

@router.post("/")
async def teacher_action(request: TeacherRequest):
    """
    Routes requests to the appropriate teacher mode function.
    """
    # The teacher_llm_request returns a dictionary that is a request for an LLM
    # We will just return that dictionary for now.
    llm_request = teacher_llm_request(
        action=request.action,
        payload=request.payload,
        session_state=request.session_state
    )

    if llm_request.get("error"):
        raise HTTPException(status_code=400, detail=llm_request.get("reason"))

    return llm_request
