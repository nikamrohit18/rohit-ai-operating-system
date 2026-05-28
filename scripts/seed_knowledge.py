"""Seed Rohit's knowledge base into Qdrant. Run: python scripts/seed_knowledge.py"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client.models import Filter, FieldCondition, MatchValue, FilterSelector
from memory.vector_store import VectorStore, COLLECTION_NAME


def seed():
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "rohit_knowledge.json")
    with open(data_path) as f:
        items = json.load(f)

    print("Connecting to Qdrant and loading embedding model...")
    vs = VectorStore()

    # Remove previously seeded items so re-runs don't create duplicates
    vs.client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=FilterSelector(
            filter=Filter(must=[FieldCondition(key="source", match=MatchValue(value="seed"))])
        ),
    )
    print("Cleared existing seed data.\n")

    print(f"Seeding {len(items)} knowledge items...\n")
    for i, item in enumerate(items, 1):
        vs.upsert(item["text"], {"category": item["category"], "source": "seed"})
        print(f"[{i}/{len(items)}] {item['category']}: {item['text'][:70]}...")

    print(f"\nDone. {len(items)} items loaded into Qdrant collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed()
