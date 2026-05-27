from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from database.models import get_conversations, get_session
from logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
templates = Jinja2Templates(directory="templates")


@router.get("/report/{session_id}", response_class=HTMLResponse, tags=["Report"])
async def render_report(session_id: str, request: Request) -> HTMLResponse:
    """
    Renders the interview report page for a completed session.

    Fetches session metadata and the full conversation history, then pairs each
    AI question with its corresponding user answer for display in the report
    template.
    """
    logger.info("Rendering report for session: %s", session_id)

    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    conversations = await get_conversations(session_id)

    # Build ordered Q&A pairs for the template
    ai_entries = {entry["question_no"]: entry for entry in conversations if entry["role"] == "ai"}
    user_entries = {entry["question_no"]: entry for entry in conversations if entry["role"] == "user"}

    qa_pairs = []
    for q_no in sorted(ai_entries.keys()):
        ai_entry = ai_entries[q_no]
        user_entry = user_entries.get(q_no)
        qa_pairs.append({
            "question_no": q_no,
            "taxonomy_level": ai_entry.get("taxonomy_level", "N/A"),
            "question": ai_entry["content"],
            "answer": user_entry["content"] if user_entry else "No answer provided",
            "score": user_entry.get("score") if user_entry else 0,
            "feedback": user_entry.get("evaluation_feedback", "") if user_entry else "",
        })

    return templates.TemplateResponse(
        request,
        "report.html",
        {
            "session": session,
            "qa_pairs": qa_pairs,
        },
    )
