from pydantic import BaseModel


class AnswerRequest(BaseModel):
    """Request payload for submitting a candidate's answer."""

    answer_text: str


class QuestionResponse(BaseModel):
    """Response payload carrying the next interview question."""

    session_id: str
    question_no: int
    question_text: str
    taxonomy_level: str
    is_complete: bool = False


class InterviewCompleteResponse(BaseModel):
    """Response payload signalling that all questions have been answered."""

    session_id: str
    is_complete: bool = True
    message: str = "Interview completed successfully"
