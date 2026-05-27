import traceback

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import get_settings
from database.models import log_error
from logger import get_logger
from constants import SARVAM_LANGUAGE_CODE, SARVAM_TTS_MODEL, SARVAM_TTS_SPEAKER, SARVAM_TTS_URL

router = APIRouter()
logger = get_logger(__name__)


class TextToSpeechRequest(BaseModel):
    text: str


class TextToSpeechResponse(BaseModel):
    audio_base64: str
    content_type: str = "audio/wav"


@router.post("/text-to-speech", response_model=TextToSpeechResponse, tags=["TTS"])
async def convert_text_to_speech(request: TextToSpeechRequest) -> TextToSpeechResponse:
    """
    Converts a text string to speech using the Sarvam AI TTS API.

    Returns base64-encoded WAV audio that the browser can decode and play
    without any additional server round-trips.
    """
    logger.info("TTS request — text preview: '%s...'", request.text[:60])
    settings = get_settings()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                SARVAM_TTS_URL,
                headers={
                    "api-subscription-key": settings.sarvam_api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "inputs": [request.text],
                    "target_language_code": SARVAM_LANGUAGE_CODE,
                    "speaker": SARVAM_TTS_SPEAKER,
                    "model": SARVAM_TTS_MODEL,
                },
            )
            response.raise_for_status()

        data = response.json()
        # Sarvam returns a list; take the first element
        audio_base64: str = data.get("audios", [""])[0]

        logger.info("TTS conversion successful")
        return TextToSpeechResponse(audio_base64=audio_base64)

    except httpx.HTTPStatusError as exc:
        logger.error("Sarvam TTS API returned %d: %s", exc.response.status_code, exc.response.text)
        await log_error(
            error_type="TTSAPIError",
            error_message=f"Sarvam TTS HTTP {exc.response.status_code}: {exc.response.text}",
            stack_trace=traceback.format_exc(),
        )
        raise HTTPException(status_code=502, detail="Text-to-speech service unavailable")

    except Exception as exc:
        logger.error("TTS conversion failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to convert text to speech")
