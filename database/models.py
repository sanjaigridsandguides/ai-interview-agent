import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiosqlite

from config import get_settings
from logger import get_logger

logger = get_logger(__name__)


def _db_path() -> str:
    return get_settings().database_path


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


async def create_session(
    name: str,
    job_role: str,
    highest_qualification: str,
    experience: str,
    skills_set: str,
) -> str:
    """
    Inserts a new candidate session and returns the generated session_id.
    """
    session_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(_db_path()) as db:
        await db.execute(
            """
            INSERT INTO sessions
                (session_id, name, job_role, highest_qualification,
                 experience, skills_set, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, name, job_role, highest_qualification, experience, skills_set, timestamp),
        )
        await db.commit()

    logger.info("Session created: %s for candidate '%s'", session_id, name)
    return session_id


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches a single session record by session_id.
    Returns a dict of column values, or None if not found.
    """
    async with aiosqlite.connect(_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def update_session_completion(
    session_id: str,
    overall_score: float,
    hire_recommendation: str,
) -> None:
    """
    Marks a session as completed with the computed overall score and hire recommendation.
    """
    async with aiosqlite.connect(_db_path()) as db:
        await db.execute(
            """
            UPDATE sessions
            SET overall_score       = ?,
                hire_recommendation = ?,
                is_completed        = 1
            WHERE session_id = ?
            """,
            (overall_score, hire_recommendation, session_id),
        )
        await db.commit()

    logger.info(
        "Session %s completed — score: %.1f, recommendation: %s",
        session_id, overall_score, hire_recommendation,
    )


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------


async def save_conversation_entry(
    session_id: str,
    question_no: int,
    role: str,
    content: str,
    taxonomy_level: Optional[str] = None,
    score: Optional[float] = None,
    evaluation_feedback: Optional[str] = None,
) -> None:
    """
    Saves a single conversation turn (AI question or user answer) to the DB.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(_db_path()) as db:
        await db.execute(
            """
            INSERT INTO conversations
                (session_id, question_no, role, content,
                 taxonomy_level, score, evaluation_feedback, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, question_no, role, content,
             taxonomy_level, score, evaluation_feedback, timestamp),
        )
        await db.commit()

    logger.debug(
        "Conversation saved — session: %s, Q%d, role: %s",
        session_id, question_no, role,
    )


async def get_conversations(session_id: str) -> List[Dict[str, Any]]:
    """Returns all conversation entries for a session ordered by question number."""
    async with aiosqlite.connect(_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM conversations WHERE session_id = ? ORDER BY question_no, id",
            (session_id,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_ai_question_count(session_id: str) -> int:
    """Returns the number of AI questions asked in a session so far."""
    async with aiosqlite.connect(_db_path()) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM conversations WHERE session_id = ? AND role = 'ai'",
            (session_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row else 0


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


async def log_error(
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    session_id: Optional[str] = None,
) -> None:
    """Saves a runtime error to the errors table."""
    timestamp = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(_db_path()) as db:
        await db.execute(
            """
            INSERT INTO errors
                (session_id, error_type, error_message, stack_trace, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, error_type, error_message, stack_trace, timestamp),
        )
        await db.commit()

    logger.error("Error logged [%s]: %s", error_type, error_message)
