from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import sys
sys.path.append('/mnt/c/Users/Lenovo/ai_study_assistant_backend')

# Now importing from the actual practice.py
from app.teacher.modes.practice import practice_llm_request
from app.logic.scheduler import build_topics_from_payload, Topic

router = APIRouter()

# In-memory session store - This should be shared across all routes.
# For now, we'll use a local one (simulating shared by modifying directly).
sessions: Dict[str, Dict[str, Any]] = {}

class PracticeRequest(BaseModel):
    action: str
    payload: Dict[str, Any]
    session_id: str

@router.post("/action")
async def practice_action(request: PracticeRequest):
    """
    Routes requests to the appropriate practice mode function.
    """
    session_id = request.session_id
    if session_id not in sessions:
        # For testing, create a dummy session with topics.
        dummy_topics = build_topics_from_payload([
            {"topic_name": "Normalization", "subject_name": "Databases", "difficulty": "medium", "weight": "high", "weakness": "weak"},
            {"topic_name": "SQL Joins", "subject_name": "Databases", "difficulty": "hard", "weight": "high", "weakness": "moderate"}
        ])
        sessions[session_id] = {"topics": dummy_topics, "plan": None, "practice_stats": {}}

    session_state = sessions[session_id]

    # practice_llm_request modifies session_state directly for practice_stats
    llm_request = practice_llm_request(
        action=request.action,
        payload=request.payload,
        session_state=session_state
    )

    if llm_request.get("error"):
        raise HTTPException(status_code=400, detail=llm_request.get("reason"))

    return llm_request
