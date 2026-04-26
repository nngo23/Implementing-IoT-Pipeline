"""
transcribe_audio.py

Whisper model is loaded ONCE at module import (server startup).
Every subsequent call reuses the same in-memory model — eliminates
the 1-3 s cold-start penalty on the first request.
"""
import logging
import os
import tempfile

import whisper
from pydub import AudioSegment

from app.config import Config
from app.utils.parsers import correct_words

logger = logging.getLogger(__name__)

_NATIVE_FORMATS = {".wav", ".flac", ".aiff", ".aif"}

# ── Load once at import time ──────────────────────────────────────────────────
logger.info("Loading Whisper model '%s' …", Config.WHISPER_MODEL)
_whisper_model = whisper.load_model(Config.WHISPER_MODEL)
logger.info("Whisper model ready.")


def transcribe_audio(audio_path: str) -> str:
    """
    Convert audio to 16 kHz mono WAV if needed, then transcribe with
    the pre-loaded Whisper model. Returns corrected plain text.
    """
    converted_path: str | None = None
    try:
        ext = os.path.splitext(audio_path)[1].lower()
        if ext not in _NATIVE_FORMATS:
            audio = AudioSegment.from_file(audio_path)
            audio = (
                audio
                .set_frame_rate(16_000)
                .set_channels(1)
                .set_sample_width(2)
            )
            fd, converted_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            audio.export(converted_path, format="wav")
            load_path = converted_path
        else:
            load_path = audio_path

        result = _whisper_model.transcribe(
            load_path,
            language="en",
            fp16=False,          # CPU-safe; set True only if CUDA available
        )
        return correct_words(result["text"].strip())

    except Exception as exc:
        raise RuntimeError(f"Transcription failed: {exc}") from exc

    finally:
        if converted_path and os.path.exists(converted_path):
            try:
                os.unlink(converted_path)
            except OSError:
                pass