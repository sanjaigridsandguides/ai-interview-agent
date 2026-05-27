from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from api.conversation import router as conversation_router
from api.interview import router as interview_router
from api.report import router as report_router
from api.session import router as session_router
from api.stt import router as stt_router
from api.tts import router as tts_router
from config import get_settings
from constants import EDUCATION_QUALIFICATIONS, JOB_ROLES
from database.connection import initialize_database
from logger import get_logger

logger = get_logger(__name__)
templates = Jinja2Templates(directory="templates")

# Initialise database tables before the server starts accepting requests
initialize_database()

app = FastAPI(
    title="AI Interview Agent",
    description=(
        "Automated technical interview system powered by LangGraph, "
        "Groq LLM (structured output), and Sarvam AI TTS/STT."
    ),
    version="1.0.0",
)

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(session_router)
app.include_router(conversation_router)
app.include_router(interview_router)
app.include_router(tts_router)
app.include_router(stt_router)
app.include_router(report_router)


# ── Page Routes ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def registration_page(request: Request) -> HTMLResponse:
    """Renders Screen 1 — candidate registration form."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "job_roles": JOB_ROLES,
            "education_qualifications": EDUCATION_QUALIFICATIONS,
        },
    )


@app.get("/interview/{session_id}", response_class=HTMLResponse)
async def interview_page(session_id: str, request: Request) -> HTMLResponse:
    """Renders Screen 2 — the live interview interface."""
    return templates.TemplateResponse(
        request,
        "interview.html",
        {
            "session_id": session_id,
        },
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
        log_level=settings.log_level.lower(),
    )
