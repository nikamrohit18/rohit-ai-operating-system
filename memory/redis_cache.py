import json
from typing import Any, Optional
import redis
from config import get_settings


class RedisCache:
    def __init__(self):
        self._client = redis.from_url(get_settings().redis_url, decode_responses=True)

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        self._client.setex(key, ttl, json.dumps(value))

    def get(self, key: str) -> Optional[Any]:
        data = self._client.get(key)
        return json.loads(data) if data else None

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def exists(self, key: str) -> bool:
        return bool(self._client.exists(key))

    def get_history(self, session_id: str, limit: int = 10) -> list:
        data = self.get(f"conv:{session_id}")
        return data[-limit:] if data else []

    def append_to_history(self, session_id: str, role: str, content: str, ttl: int = 86400) -> None:
        key = f"conv:{session_id}"
        history = self.get(key) or []
        history.append({"role": role, "content": content})
        self.set(key, history, ttl=ttl)
