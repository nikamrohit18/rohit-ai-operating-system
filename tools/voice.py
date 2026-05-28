import httpx
from config import get_settings


def text_to_speech(text: str) -> bytes:
    """Convert text to MP3 audio via ElevenLabs. Returns b'' if key not configured."""
    settings = get_settings()
    if not settings.elevenlabs_api_key:
        return b""

    response = httpx.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}",
        headers={"xi-api-key": settings.elevenlabs_api_key, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        },
        timeout=30,
    )
    if not response.is_success:
        raise ValueError(f"ElevenLabs {response.status_code}: {response.text}")
    return response.content
