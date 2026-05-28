from functools import lru_cache
from memory.postgres import get_session
from memory.redis_cache import RedisCache
from memory.vector_store import VectorStore
from sqlalchemy.orm import Session


def get_db():
    session = get_session()
    try:
        yield session
    finally:
        session.close()


@lru_cache
def get_redis() -> RedisCache:
    return RedisCache()


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore()
