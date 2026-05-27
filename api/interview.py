import traceback
from typing import Union

from fastapi import APIRouter, HTTPException

from agent.graph import create_interview_graph
from agent.state import InterviewState
from database.models import log_error
from logger import get_logger
from schemas.interview import AnswerRequest, InterviewCompleteResponse, QuestionResponse

router = APIRouter()
logger = get_logger(__name__)

# Compile the graph once at module load time so subsequent requests reuse the
# same compiled object and avoid recompilation overhead.
_interview_graph = create_interview_graph()


@router.post(
    "/interview/start/{session_id}",
    response_model=QuestionResponse,
    tags=["Interview"],
)
async def start_interview(session_id: str) -> QuestionResponse:
    """
    Kicks off an interview session and returns the first question.

    Runs the agent in ``'start'`` mode:
      fetch_session → generate_question → END

    The first question always targets Bloom's Level 1 (Remember).
    """
    logger.info("Starting interview for session: %s", session_id)

    try:
        initial_state: InterviewState = _build_initial_state(session_id, mode="start")
        final_state = await _interview_graph.ainvoke(initial_state)

        if final_state.get("error"):
            raise HTTPException(status_code=404, detail=final_state["error"])

        return QuestionResponse(
            session_id=session_id,
            question_no=1,
            question_text=final_state["current_question"],
            taxonomy_level=final_state["current_taxonomy_level"],
            is_complete=False,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to start interview %s: %s", session_id, exc)
        await log_error(
            error_type="InterviewStartError",
            error_message=str(exc),
            stack_trace=traceback.format_exc(),
            session_id=session_id,
        )
        raise HTTPException(status_code=500, detail="Failed to start interview")


@router.post(
    "/interview/answer/{session_id}",
    response_model=Union[QuestionResponse, InterviewCompleteResponse],
    tags=["Interview"],
)
async def submit_answer(
    session_id: str,
    request: AnswerRequest,
) -> Union[QuestionResponse, InterviewCompleteResponse]:
    """
    Accepts a candidate's answer, evaluates it, and returns the next question.

    Runs the agent in ``'answer'`` mode:
      fetch_session → evaluate_answer → generate_question (or generate_report) → END

    Returns ``InterviewCompleteResponse`` when all 6 questions have been answered,
    otherwise returns the next ``QuestionResponse``.
    """
    logger.info("Processing answer for session: %s", session_id)

    try:
        initial_state: InterviewState = _build_initial_state(
            session_id, mode="answer", answer_text=request.answer_text
        )
        final_state = await _interview_graph.ainvoke(initial_state)

        if final_state.get("error"):
            raise HTTPException(status_code=400, detail=final_state["error"])

        if final_state["is_interview_complete"]:
            return InterviewCompleteResponse(session_id=session_id)

        return QuestionResponse(
            session_id=session_id,
            question_no=final_state["current_question_no"] - 1,
            question_text=final_state["current_question"],
            taxonomy_level=final_state["current_taxonomy_level"],
            is_complete=False,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to process answer for session %s: %s", session_id, exc)
        await log_error(
            error_type="InterviewAnswerError",
            error_message=str(exc),
            stack_trace=traceback.format_exc(),
            session_id=session_id,
        )
        raise HTTPException(status_code=500, detail="Failed to process answer")


def _build_initial_state(
    session_id: str,
    mode: str,
    answer_text: str = None,
) -> InterviewState:
    """Constructs a blank InterviewState to seed each graph invocation."""
    return InterviewState(
        session_id=session_id,
        mode=mode,
        answer_text=answer_text,
        session_data=None,
        conversation_history=None,
        current_question_no=1,
        current_question=None,
        current_taxonomy_level=None,
        evaluation_score=None,
        evaluation_feedback=None,
        final_report=None,
        is_interview_complete=False,
        error=None,
    )
