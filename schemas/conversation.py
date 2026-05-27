from typing import Optional
from pydantic import BaseModel


class SaveQuestionRequest(BaseModel):
    """Request payload for saving an AI-generated question to the conversations table."""

    session_id: str
    question_no: int
    content: str
    taxonomy_level: str


class SaveAnswerRequest(BaseModel):
    """Request payload for saving a candidate's evaluated answer to the conversations table."""

    session_id: str
    question_no: int
    content: str
    score: float
    evaluation_feedback: str


class SaveConversationResponse(BaseModel):
    """Response payload returned after a conversation entry is successfully saved."""

    message: str = "Saved successfully"
