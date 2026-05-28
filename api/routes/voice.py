from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from tools.voice import text_to_speech
from memory.postgres import get_session, Task

router = APIRouter(prefix="/voice", tags=["voice"])


class VoiceRequest(BaseModel):
    text: str


@router.post("/")
async def synthesize(payload: VoiceRequest):
    """Convert text to speech. Returns MP3 audio."""
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    try:
        audio = text_to_speech(payload.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ElevenLabs error: {str(e)}")
    if not audio:
        raise HTTPException(status_code=503, detail="ElevenLabs API key not configured")
    return Response(content=audio, media_type="audio/mpeg")


@router.get("/task/{task_id}")
async def synthesize_task(task_id: str):
    """Synthesize the output of a completed task as speech."""
    session = get_session()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
    finally:
        session.close()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.output:
        raise HTTPException(status_code=400, detail="Task has no output yet")

    text = task.output[:5000]
    try:
        audio = text_to_speech(text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ElevenLabs error: {str(e)}")
    if not audio:
        raise HTTPException(status_code=503, detail="ElevenLabs API key not configured")
    return Response(content=audio, media_type="audio/mpeg")
