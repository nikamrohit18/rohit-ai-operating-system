import uuid
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from fastembed import TextEmbedding
from config import get_settings

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
VECTOR_SIZE = 384
COLLECTION_NAME = "rohit_knowledge"


class VectorStore:
    def __init__(self):
        settings = get_settings()
        self.client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        self.encoder = TextEmbedding(EMBEDDING_MODEL)
        self._ensure_collection()

    def _ensure_collection(self):
        existing = {c.name for c in self.client.get_collections().collections}
        if COLLECTION_NAME not in existing:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )

    def embed(self, text: str) -> List[float]:
        return list(self.encoder.embed([text]))[0].tolist()

    def upsert(self, text: str, metadata: dict) -> str:
        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(id=point_id, vector=self.embed(text), payload={**metadata, "text": text})],
        )
        return point_id

    def search(self, query: str, limit: int = 5, filter_by: Optional[dict] = None) -> List[dict]:
        search_filter = None
        if filter_by:
            conditions = [FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filter_by.items()]
            search_filter = Filter(must=conditions)

        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=self.embed(query),
            limit=limit,
            query_filter=search_filter,
        )
        return [{"text": r.payload.get("text", ""), "metadata": r.payload, "score": r.score} for r in results.points]
