from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.teacher.modes.teacher_mode import teacher_llm_request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class TeacherModeRequest(BaseModel):
    action: str
    payload: Dict[str, Any]
    session_state: Dict[str, Any]

@router.post("/")
async def teacher_mode(body: TeacherModeRequest):
    """
    Handles various teacher mode actions by delegating to the teacher_llm_request function.
    """
    try:
        logger.info(f"Received teacher mode request with action: {body.action}")
        logger.debug(f"Payload: {body.payload}")
        logger.debug(f"Session State: {body.session_state}")

        # Validate that the action is a non-empty string
        if not body.action or not isinstance(body.action, str):
            raise HTTPException(status_code=400, detail="Invalid action provided.")

        # Delegate the request to the core logic
        response = teacher_llm_request(body.action, body.payload, body.session_state)
        
        logger.info(f"Successfully processed teacher mode action: {body.action}")
        return response

    except HTTPException as http_exc:
        logger.error(f"HTTP exception in teacher mode: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"An unexpected error occurred in teacher mode: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")

