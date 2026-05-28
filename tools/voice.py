import re
import httpx
from config import get_settings


def clean_for_speech(text: str) -> str:
    text = re.sub(r'#{1,6}\s*', '', text)           # ## headings
    text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)  # **bold** / *italic*
    text = re.sub(r'`{1,3}[^`]*`{1,3}', '', text)  # `code` / ```blocks```
    text = re.sub(r'^\s*[-*•]\s+', '', text, flags=re.MULTILINE)  # bullet points
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [links](url)
    text = re.sub(r'[^\x00-\x7F]', '', text)        # emojis and non-ASCII
    text = re.sub(r'\n{3,}', '\n\n', text)          # excessive newlines
    return text.strip()


def text_to_speech(text: str) -> bytes:
    """Convert text to MP3 audio via ElevenLabs. Returns b'' if key not configured."""
    settings = get_settings()
    if not settings.elevenlabs_api_key:
        return b""

    text = clean_for_speech(text)
    if not text:
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
