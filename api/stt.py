import traceback

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from config import get_settings
from database.models import log_error
from logger import get_logger
from constants import SARVAM_LANGUAGE_CODE, SARVAM_STT_URL

router = APIRouter()
logger = get_logger(__name__)


class SpeechToTextResponse(BaseModel):
    text: str


@router.post("/speech-to-text", response_model=SpeechToTextResponse, tags=["STT"])
async def convert_speech_to_text(audio: UploadFile = File(...)) -> SpeechToTextResponse:
    """
    Transcribes a candidate's audio answer using the Sarvam AI STT API.

    Accepts a multipart audio file upload (WebM, WAV, MP3, etc.) and returns
    the transcribed text string.
    """
    logger.info("STT request — filename: %s, content-type: %s", audio.filename, audio.content_type)
    settings = get_settings()

    try:
        audio_bytes = await audio.read()

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                SARVAM_STT_URL,
                headers={"api-subscription-key": settings.sarvam_api_key},
                files={"file": (audio.filename or "audio.webm", audio_bytes, audio.content_type)},
                data={"language_code": SARVAM_LANGUAGE_CODE},
            )
            response.raise_for_status()

        data = response.json()
        transcript: str = data.get("transcript", "")

        logger.info("STT transcription complete — preview: '%s...'", transcript[:80])
        return SpeechToTextResponse(text=transcript)

    except httpx.HTTPStatusError as exc:
        logger.error("Sarvam STT API returned %d: %s", exc.response.status_code, exc.response.text)
        await log_error(
            error_type="STTAPIError",
            error_message=f"Sarvam STT HTTP {exc.response.status_code}: {exc.response.text}",
            stack_trace=traceback.format_exc(),
        )
        raise HTTPException(status_code=502, detail="Speech-to-text service unavailable")

    except Exception as exc:
        logger.error("STT conversion failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to convert speech to text")
