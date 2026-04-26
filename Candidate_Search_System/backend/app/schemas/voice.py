from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class VoiceRequest(BaseModel):
    text: str = Field(..., description="Converted text content to process")


class VoiceResponse(BaseModel):
    success: bool = Field(
        ..., description="True when transcription and validation passed"
    )

    transcription: Optional[str] = Field(
        None, description="Whisper transcription"
    )

    payload: Optional[Dict[str, Any]] = Field(
        None, description="Parsed search parameters"
    )

    # ⚠️ SHORT + STRICT (NO 'try again' TEXT)
    warning: Optional[str] = Field(
        None,
        description="Short validation message when role or industry is missing"
    )

    # 🔥 Frontend control flag
    block_stream: bool = Field(
        False,
        description="If True, frontend must NOT call search endpoint"
    )

    n8n_response: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None
    
