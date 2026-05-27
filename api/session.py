import traceback

from fastapi import APIRouter, HTTPException

from database.models import (
    create_session,
    get_ai_question_count,
    get_conversations,
    get_session,
    log_error,
)
from logger import get_logger
from schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
    SessionDetailResponse,
)

router = APIRouter()
logger = get_logger(__name__)


@router.post("/session/create", response_model=CreateSessionResponse, tags=["Session"])
async def create_interview_session(request: CreateSessionRequest) -> CreateSessionResponse:
    """
    Creates a new interview session for a candidate.

    Persists the candidate's profile to the database and returns a unique
    session_id that must be supplied to all subsequent interview endpoints.
    """
    logger.info("Creating session for candidate: '%s' | Role: %s", request.name, request.job_role)

    try:
        session_id = await create_session(
            name=request.name,
            job_role=request.job_role,
            experience=request.experience,
            highest_qualification=request.highest_qualification,
            skills_set=request.skills_set,
        )
        return CreateSessionResponse(session_id=session_id)

    except Exception as exc:
        logger.error("Failed to create session: %s", exc)
        await log_error(
            error_type="SessionCreationError",
            error_message=str(exc),
            stack_trace=traceback.format_exc(),
        )
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("/session/{session_id}", response_model=SessionDetailResponse, tags=["Session"])
async def get_session_details(session_id: str) -> SessionDetailResponse:
    """
    Fetches the full session details for a given session_id.

    Returns the candidate profile, entire conversation history, and the number
    of AI questions asked so far. This endpoint is called by the fetch_session
    node inside the LangGraph agent at the start of every graph run.
    """
    logger.info("Fetching session details for: %s", session_id)

    session_data = await get_session(session_id)

    if not session_data:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    conversation_history = await get_conversations(session_id)
    question_count = await get_ai_question_count(session_id)

    logger.info(
        "Session details fetched — candidate: '%s', questions asked: %d",
        session_data["name"], question_count,
    )

    return SessionDetailResponse(
        session_data=session_data,
        conversation_history=conversation_history,
        question_count=question_count,
    )
