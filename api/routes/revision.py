from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import sys
sys.path.append('/mnt/c/Users/Lenovo/ai_study_assistant_backend')

# Now importing from the actual revision.py
from app.teacher.modes.revision import revision_llm_request
from app.logic.scheduler import build_topics_from_payload, Topic

router = APIRouter()

# In-memory session store - This should be shared across all routes.
# For now, we'll use a local one (simulating shared by modifying directly).
sessions: Dict[str, Dict[str, Any]] = {}

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