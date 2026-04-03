from pydantic import BaseModel, Field
from typing import Optional, Dict, Any ,List

class VoiceRequest(BaseModel):
    text: str = Field(..., description="The converted text content to be processed")

class VoiceResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the voice processing was successful")
    transcription: Optional[str] = Field(..., description="The transcribed text from the voice input")
    payload: Optional[Dict[str, Any]] = None
    n8n_response: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None
    
