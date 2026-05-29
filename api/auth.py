from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from config import get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(key: str = Security(_api_key_header)):
    settings = get_settings()
    if not settings.api_key:
        return
    if key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
