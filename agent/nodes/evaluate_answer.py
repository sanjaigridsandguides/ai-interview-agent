import httpx

from agent.state import InterviewState
from config import get_settings
from database.models import update_session_completion
from logger import get_logger
from services.llm_service import evaluate_candidate_answer
from constants import HIRE_THRESHOLDS, TOTAL_QUESTIONS

logger = get_logger(__name__)


async def evaluate_answer_node(state: InterviewState) -> InterviewState:
    """
    Evaluates the candidate's answer and saves the result via the conversation API.

    If this was the last question (Q6), it also computes the overall score,
    determines the hire recommendation from thresholds, and marks the session
    as completed — all in one place, no extra node needed.
    """
    settings = get_settings()
    session_data = state["session_data"]
    conversation_history = state["conversation_history"] or []
    answer_text = state["answer_text"] or ""

    # Find the most recent AI question in the conversation history
    last_ai_entry = next(
        (entry for entry in reversed(conversation_history) if entry["role"] == "ai"),
        None,
    )

    if not last_ai_entry:
        logger.error("No AI question found in history for session: %s", state["session_id"])
        return {**state, "error": "No question found in history to evaluate against"}

    question_no = last_ai_entry["question_no"]
    question_text = last_ai_entry["content"]
    taxonomy_level = last_ai_entry.get("taxonomy_level", "Unknown")

    logger.info("Evaluating answer for Q%d (%s)", question_no, taxonomy_level)

    result = await evaluate_candidate_answer(
        session_data=session_data,
        question_text=question_text,
        answer_text=answer_text,
        taxonomy_level=taxonomy_level,
        groq_api_key=settings.groq_api_key,
    )

    # Save the answer via the conversation API
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(
            f"http://localhost:{settings.app_port}/conversation/answer",
            json={
                "session_id": state["session_id"],
                "question_no": question_no,
                "content": answer_text,
                "score": result.score,
                "evaluation_feedback": result.evaluation_feedback,
            },
        )

    logger.info("Q%d answer evaluated — score: %.1f/10", question_no, result.score)

    # ── If this was the last question, complete the session ──────────────────
    is_last_question = question_no == TOTAL_QUESTIONS

    if is_last_question:
        # Compute overall score from all saved answers (including this one)
        all_answers = [entry for entry in conversation_history if entry["role"] == "user"]
        all_scores = [entry["score"] for entry in all_answers if entry.get("score") is not None]
        all_scores.append(result.score)

        overall_score = round(sum(all_scores) / len(all_scores), 2)

        # Pick hire recommendation using the threshold table from constants
        hire_recommendation = "Not Recommended"
        for label, threshold in sorted(HIRE_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
            if overall_score >= threshold:
                hire_recommendation = label
                break

        await update_session_completion(
            session_id=state["session_id"],
            overall_score=overall_score,
            hire_recommendation=hire_recommendation,
        )

        logger.info(
            "Interview complete — overall score: %.2f, recommendation: %s",
            overall_score, hire_recommendation,
        )

    return {
        **state,
        "current_question_no": question_no + 1,
        "evaluation_score": result.score,
        "evaluation_feedback": result.evaluation_feedback,
        "is_interview_complete": is_last_question,
    }
