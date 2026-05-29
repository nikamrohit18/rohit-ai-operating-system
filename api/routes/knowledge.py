from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from memory.vector_store import VectorStore
from memory.postgres import get_session, KnowledgeItem
from api.auth import require_api_key

router = APIRouter(prefix="/knowledge", tags=["knowledge"], dependencies=[Depends(require_api_key)])

_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store


class KnowledgeCreate(BaseModel):
    text: str
    category: str = "general"
    source: str = "manual"


@router.post("/", status_code=201)
async def add_knowledge(payload: KnowledgeCreate):
    """Add a knowledge item to Qdrant and record it in PostgreSQL."""
    store = get_store()
    vector_id = store.upsert(payload.text, {"category": payload.category, "source": payload.source})

    session = get_session()
    try:
        item = KnowledgeItem(
            content=payload.text,
            source=payload.source,
            metadata_={"category": payload.category},
            vector_id=vector_id,
        )
        session.add(item)
        session.commit()
        return {"id": item.id, "vector_id": vector_id, "category": payload.category}
    finally:
        session.close()


@router.get("/search")
async def search_knowledge(q: str, limit: int = 5):
    """Semantic search over Rohit's knowledge base."""
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    results = get_store().search(q, limit=limit)
    return {"query": q, "results": results}


@router.get("/")
async def list_knowledge(limit: int = 50):
    """List all knowledge items from PostgreSQL."""
    session = get_session()
    try:
        items = session.query(KnowledgeItem).order_by(KnowledgeItem.created_at.desc()).limit(limit).all()
        return [
            {
                "id": i.id,
                "content": i.content,
                "source": i.source,
                "category": (i.metadata_ or {}).get("category"),
                "created_at": i.created_at.isoformat(),
            }
            for i in items
        ]
    finally:
        session.close()
