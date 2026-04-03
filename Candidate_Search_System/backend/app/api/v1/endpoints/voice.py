from fastapi import APIRouter, HTTPException, File, UploadFile, Query
from fastapi.responses import JSONResponse
from app.schemas.voice import VoiceRequest, VoiceResponse
from app.core.transcribe_audio import transcribe_audio
from app.utils.parsers import INDUSTRY_MAP, parse_voice_command
import tempfile
import time
import requests
import os
from typing import Dict, Any, Optional 
from app.config import Config


router = APIRouter()

N8N_WEBHOOK_URL = Config.N8N_WEBHOOK_URL
WHISPER_MODEL = Config.WHISPER_MODEL

def send_to_n8n(payload: Dict[str, Any]) -> Dict[str, Any]:

    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response.raise_for_status()
        
        try:
            return response.json()
        except:
            return {"status": "success", "raw": response.text}
            
    except requests.exceptions.ConnectionError:
        raise Exception(f"Cannot connect to n8n at {N8N_WEBHOOK_URL}")
    except requests.exceptions.Timeout:
        raise Exception("n8n request timeout")
    except Exception as e:
        raise Exception(f"n8n request failed: {str(e)}")


@router.get("/voice_health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "whisper_model": WHISPER_MODEL,
        "n8n_webhook": N8N_WEBHOOK_URL,
        "supported_industries": list(set(INDUSTRY_MAP.values()))
    }

@router.post("/voice", response_model=VoiceResponse)
async def parse_voice(audio: UploadFile = File(...), output_channel: str = Query("slack", description="Output channel: slack or email"),recipient_email: Optional[str] = Query(None, description="Recipient email address")):
    start_time = time.time()
    
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(400, "File must be audio format")
    
    tmp_path = None
    
    try:
        # Step 1: Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Step 2: Transcribe
        text = transcribe_audio(tmp_path)
        
        # Step 3: Parse parameters
        payload = parse_voice_command(text, output_channel, recipient_email)
        
        # Step 4: Send to n8n
        n8n_response = send_to_n8n(payload)
        
        processing_time = time.time() - start_time
        
        return VoiceResponse(
            success=True,
            transcription=text,
            payload=payload,
            n8n_response=n8n_response,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(500, str(e))
        
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
