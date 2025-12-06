from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from app.teacher.modes.revision import revision_llm_request
from app.logic.scheduler import build_topics_from_payload, Topic

router = APIRouter()

class RevisionRequest(BaseModel):
    action: str
    payload: Dict[str, Any]
    session_state: Dict[str, Any]

@router.post("/")
async def revision_action(request: RevisionRequest):
    """
    Routes requests to the appropriate revision/exam mode function.
    """
    llm_request = revision_llm_request(
        action=request.action,
        payload=request.payload,
        session_state=request.session_state
    )

    if llm_request.get("error"):
        raise HTTPException(status_code=400, detail=llm_request.get("reason"))

    return llm_request
