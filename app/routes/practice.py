from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from app.teacher.modes.practice import practice_llm_request
from app.logic.scheduler import build_topics_from_payload, Topic

router = APIRouter()

class PracticeRequest(BaseModel):
    action: str
    payload: Dict[str, Any]
    session_state: Dict[str, Any]

@router.post("/")
async def practice_action(request: PracticeRequest):
    """
    Routes requests to the appropriate practice mode function.
    """
    # practice_llm_request modifies session_state directly for practice_stats
    llm_request = practice_llm_request(
        action=request.action,
        payload=request.payload,
        session_state=request.session_state
    )

    if llm_request.get("error"):
        raise HTTPException(status_code=400, detail=llm_request.get("reason"))

    return llm_request
