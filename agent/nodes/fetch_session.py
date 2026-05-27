import httpx

from agent.state import InterviewState
from config import get_settings
from logger import get_logger

logger = get_logger(__name__)


async def fetch_session_node(state: InterviewState) -> InterviewState:
    """
    Fetches session details by calling the GET /session/{session_id} API.

    This keeps the agent decoupled from the database — it talks to the API
    layer just like any other client would, rather than importing DB functions
    directly.
    """
    session_id = state["session_id"]
    settings = get_settings()

    url = f"http://localhost:{settings.app_port}/session/{session_id}"
    logger.info("Fetching session via API: %s", url)

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)

    if response.status_code == 404:
        logger.error("Session not found: %s", session_id)
        return {**state, "error": f"Session '{session_id}' not found"}

    if response.status_code != 200:
        logger.error("Session API returned %d for session: %s", response.status_code, session_id)
        return {**state, "error": f"Failed to fetch session details (HTTP {response.status_code})"}

    data = response.json()

    logger.info(
        "Session loaded — candidate: '%s', questions asked so far: %d",
        data["session_data"]["name"], data["question_count"],
    )

    return {
        **state,
        "session_data": data["session_data"],
        "conversation_history": data["conversation_history"],
        "current_question_no": data["question_count"] + 1,
    }
