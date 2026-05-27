from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    """Request payload for creating a new interview session."""

    name: str = Field(..., min_length=2, max_length=100, description="Candidate's full name")
    job_role: str = Field(..., description="Target job role for the interview")
    experience: str = Field(..., description="Years and type of work experience")
    highest_qualification: str = Field(..., description="Highest educational qualification")
    skills_set: str = Field(..., description="Comma-separated list of candidate skills")


class CreateSessionResponse(BaseModel):
    """Response payload returned after a session is successfully created."""

    session_id: str
    message: str = "Session created successfully"


class SessionDetailResponse(BaseModel):
    """Response payload for GET /session/{session_id} used by the agent."""

    session_data: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    question_count: int
