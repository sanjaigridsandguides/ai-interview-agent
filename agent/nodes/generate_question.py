import httpx

from agent.state import InterviewState
from config import get_settings
from logger import get_logger
from services.llm_service import generate_interview_question
from constants import TAXONOMY_LEVELS

logger = get_logger(__name__)


async def generate_question_node(state: InterviewState) -> InterviewState:
    """
    Generates the next interview question at the appropriate Bloom's taxonomy level.

    The taxonomy level is determined by ``current_question_no``:
    Q1 → Remember, Q2 → Understand, … Q6 → Create.

    The generated question is saved to the conversations table before being
    returned in state so that it is durable even if the API call later fails.
    """
    settings = get_settings()
    session_data = state["session_data"]
    question_no = state["current_question_no"]

    # Pick taxonomy level (clamp to last level for safety)
    taxonomy_index = min(question_no - 1, len(TAXONOMY_LEVELS) - 1)
    taxonomy = TAXONOMY_LEVELS[taxonomy_index]

    logger.info(
        "Generating Q%d at Bloom's level %d (%s)",
        question_no, taxonomy["level"], taxonomy["name"],
    )

    history_context = _build_history_context(state.get("conversation_history") or [])

    result = await generate_interview_question(
        session_data=session_data,
        question_no=question_no,
        taxonomy=taxonomy,
        history_context=history_context,
        groq_api_key=settings.groq_api_key,
    )

    # Save the question via the conversation API
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(
            f"http://localhost:{settings.app_port}/conversation/question",
            json={
                "session_id": state["session_id"],
                "question_no": question_no,
                "content": result.question,
                "taxonomy_level": taxonomy["name"],
            },
        )

    logger.info("Q%d generated and saved — taxonomy: %s", question_no, taxonomy["name"])

    return {
        **state,
        "current_question": result.question,
        "current_taxonomy_level": taxonomy["name"],
    }


def _build_history_context(conversation_history: list) -> str:
    """Returns a formatted string of the last two Q&A exchanges for prompt context."""
    if not conversation_history:
        return "No previous conversation."

    recent = conversation_history[-4:]  # Up to last 2 Q&A pairs
    lines = []
    for entry in recent:
        speaker = "Interviewer" if entry["role"] == "ai" else "Candidate"
        lines.append(f"{speaker}: {entry['content']}")

    return "\n".join(lines)
