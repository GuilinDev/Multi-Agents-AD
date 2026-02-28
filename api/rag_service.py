"""
RAG Service — Protocol retrieval from ChromaDB.
Only retrieves, never generates care advice. Zero hallucination by design.
"""

import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base", "chroma_db")
COLLECTION_NAME = "dementia_care_guidelines"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        _collection = _client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
        )
    return _collection


def search_protocols(
    query: str,
    n_results: int = 5,
    source_filter: str | None = None,
) -> list[dict]:
    """
    Search dementia care guidelines for relevant protocol steps.
    
    Args:
        query: Natural language description of the behavioral event
        n_results: Number of results to return
        source_filter: Optional filter by source (CMS, NICE, APA, Alzheimer's Association)
    
    Returns:
        List of {text, source, title, page, score} dicts
    """
    collection = _get_collection()
    
    where_filter = None
    if source_filter:
        where_filter = {"source": source_filter}
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter,
    )
    
    output = []
    for i in range(len(results["documents"][0])):
        meta = results["metadatas"][0][i]
        distance = results["distances"][0][i] if results.get("distances") else None
        output.append({
            "text": results["documents"][0][i],
            "source": meta.get("source", "Unknown"),
            "title": meta.get("title", "Unknown"),
            "page": meta.get("page", 0),
            "filename": meta.get("filename", ""),
            "score": round(1 - distance, 4) if distance is not None else None,
        })
    
    return output


def search_by_event_type(event_type: str, n_results: int = 5) -> list[dict]:
    """
    Search protocols by behavioral event type.
    Maps common event types to optimized search queries.
    """
    query_map = {
        "agitation": "managing agitation aggressive behavior dementia non-pharmacological intervention",
        "sundowning": "sundowning late afternoon evening confusion dementia management strategies",
        "wandering": "wandering elopement prevention dementia patient safety environmental modification",
        "refusal": "medication refusal food refusal dementia patient care strategies compliance",
        "fall": "fall prevention dementia patient safety assessment risk factors intervention",
        "aggression": "aggressive behavior dementia de-escalation techniques non-pharmacological management",
        "confusion": "acute confusion delirium dementia assessment differential diagnosis management",
        "sleep_disturbance": "sleep disturbance insomnia dementia non-pharmacological sleep hygiene",
    }
    
    search_query = query_map.get(event_type.lower(), f"{event_type} dementia care management")
    return search_protocols(search_query, n_results=n_results)


if __name__ == "__main__":
    # Quick test
    print("=== RAG Service Test ===\n")
    
    results = search_protocols("patient is agitated and refusing medication")
    for i, r in enumerate(results):
        print(f"Result {i+1} [{r['source']} p.{r['page']}, score={r['score']}]:")
        print(f"  {r['text'][:150]}...")
        print()
    
    print("=== By Event Type: sundowning ===\n")
    results = search_by_event_type("sundowning", n_results=3)
    for i, r in enumerate(results):
        print(f"Result {i+1} [{r['source']} p.{r['page']}, score={r['score']}]:")
        print(f"  {r['text'][:150]}...")
        print()
