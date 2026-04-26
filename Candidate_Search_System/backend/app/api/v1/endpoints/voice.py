"""
voice.py — voice endpoint with strict role + industry gate.

Flow:
  1. Save upload → temp file
  2. Whisper transcription
  3. parse_voice_command
  4. STRICT validation gate (role + industry)
  5. Return safe payload ONLY if valid
"""

import asyncio
import logging
import os
import tempfile
import time
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.config import Config
from app.core.transcribe_audio import transcribe_audio
from app.schemas.voice import VoiceResponse
from app.utils.parsers import parse_voice_command

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/voice_health")
async def health_check():
    return {
        "status": "healthy",
        "whisper_model": Config.WHISPER_MODEL,
        "n8n_webhook": Config.N8N_WEBHOOK_URL,
    }


@router.post("/voice", response_model=VoiceResponse)
async def parse_voice(
    audio: UploadFile = File(...),
    output_channel: str = Query("slack", description="slack or email"),
    recipient_email: Optional[str] = Query(None),
):
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(400, "File must be audio format")

    start = time.time()
    tmp_path: Optional[str] = None

    try:
        # ── 1. Save upload ─────────────────────────────
        content = await audio.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # ── 2. Transcribe ─────────────────────────────
        text = await asyncio.to_thread(transcribe_audio, tmp_path)

        # ── 3. Parse command ───────────────────────────
        payload = parse_voice_command(text, output_channel, recipient_email)

        elapsed = round(time.time() - start, 2)

        role_detected = bool(payload.get("role_detected"))
        industry = payload.get("industry")

        # ───────────────────────────────────────────────
        # 🔥 HARD GATE #1 — ROLE REQUIRED
        # ───────────────────────────────────────────────
        if not role_detected:
            logger.info("BLOCKED (no role): %s", text)
            return VoiceResponse(
                success=False,
                transcription=text,
                payload=payload,
                warning="No role detected. Specify a job role like 'nurse', 'welder', 'driver', or 'software developer'.",
                processing_time=elapsed,
                block_stream=True,
            )

        # ───────────────────────────────────────────────
        # 🔥 HARD GATE #2 — INDUSTRY REQUIRED
        # ───────────────────────────────────────────────
        if not industry:
            logger.info("BLOCKED (no industry): %s", text)
            return VoiceResponse(
                success=False,
                transcription=text,
                payload=payload,
                warning="No matching industry found. Specify a clear role like 'doctor', 'nurse', 'driver', or 'engineer'.",
                processing_time=elapsed,
                block_stream=True,
            )

        # ───────────────────────────────────────────────
        # ✅ SAFE TO CONTINUE
        # ───────────────────────────────────────────────
        return VoiceResponse(
            success=True,
            transcription=text,
            payload=payload,
            n8n_response=None,
            processing_time=elapsed,
            block_stream=False,
        )

    except Exception as exc:
        logger.error("Voice processing error: %s", exc)
        raise HTTPException(500, str(exc))

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass