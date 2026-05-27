import os
import sqlite3

from config import get_settings
from logger import get_logger

logger = get_logger(__name__)


def initialize_database() -> None:
    """
    Creates all database tables if they do not already exist.

    Uses the standard sqlite3 module — no async needed since this runs
    once at startup before the server begins accepting requests.
    """
    settings = get_settings()
    db_path = settings.database_path

    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    with sqlite3.connect(db_path) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id            TEXT PRIMARY KEY,
                name                  TEXT NOT NULL,
                job_role              TEXT NOT NULL,
                highest_qualification TEXT NOT NULL,
                experience            TEXT NOT NULL,
                skills_set            TEXT NOT NULL,
                overall_score         REAL    DEFAULT 0.0,
                final_feedback        TEXT,
                hire_recommendation   TEXT,
                is_completed          INTEGER DEFAULT 0,
                timestamp             TEXT NOT NULL
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id          TEXT NOT NULL,
                question_no         INTEGER,
                role                TEXT NOT NULL,
                content             TEXT NOT NULL,
                taxonomy_level      TEXT,
                score               REAL,
                evaluation_feedback TEXT,
                timestamp           TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id    TEXT,
                error_type    TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace   TEXT,
                timestamp     TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        db.commit()

    logger.info("Database initialised at: %s", os.path.abspath(db_path))
