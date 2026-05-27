import traceback

from fastapi import APIRouter, HTTPException

from database.models import log_error, save_conversation_entry
from logger import get_logger
from schemas.conversation import (
    SaveAnswerRequest,
    SaveConversationResponse,
    SaveQuestionRequest,
)

router = APIRouter()
logger = get_logger(__name__)


@router.post("/conversation/question", response_model=SaveConversationResponse, tags=["Conversation"])
async def save_question(request: SaveQuestionRequest) -> SaveConversationResponse:
    """
    Saves an AI-generated interview question to the conversations table.

    Called by the generate_question node after the LLM produces a question,
    so the question is persisted before being returned to the frontend.
    """
    logger.info(
        "Saving question — session: %s, Q%d, taxonomy: %s",
        request.session_id, request.question_no, request.taxonomy_level,
    )

    try:
        await save_conversation_entry(
            session_id=request.session_id,
            question_no=request.question_no,
            role="ai",
            content=request.content,
            taxonomy_level=request.taxonomy_level,
        )
        return SaveConversationResponse()

    except Exception as exc:
        logger.error("Failed to save question: %s", exc)
        await log_error(
            error_type="SaveQuestionError",
            error_message=str(exc),
            stack_trace=traceback.format_exc(),
            session_id=request.session_id,
        )
        raise HTTPException(status_code=500, detail="Failed to save question")


@router.post("/conversation/answer", response_model=SaveConversationResponse, tags=["Conversation"])
async def save_answer(request: SaveAnswerRequest) -> SaveConversationResponse:
    """
    Saves a candidate's evaluated answer to the conversations table.

    Called by the evaluate_answer node after the LLM scores the answer,
    so the score and feedback are persisted alongside the answer text.
    """
    logger.info(
        "Saving answer — session: %s, Q%d, score: %.1f",
        request.session_id, request.question_no, request.score,
    )

    try:
        await save_conversation_entry(
            session_id=request.session_id,
            question_no=request.question_no,
            role="user",
            content=request.content,
            score=request.score,
            evaluation_feedback=request.evaluation_feedback,
        )
        return SaveConversationResponse()

    except Exception as exc:
        logger.error("Failed to save answer: %s", exc)
        await log_error(
            error_type="SaveAnswerError",
            error_message=str(exc),
            stack_trace=traceback.format_exc(),
            session_id=request.session_id,
        )
        raise HTTPException(status_code=500, detail="Failed to save answer")
