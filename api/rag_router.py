"""
RAG API endpoints for protocol retrieval.
These are the core Caregiver Copilot endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from rag_service import search_protocols, search_by_event_type

router = APIRouter(prefix="/api/rag", tags=["RAG Protocol Retrieval"])


class ProtocolResult(BaseModel):
    text: str
    source: str
    title: str
    page: int
    filename: str
    score: float | None


class SearchRequest(BaseModel):
    query: str
    n_results: int = 5
    source_filter: str | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[ProtocolResult]
    count: int


class EventSearchRequest(BaseModel):
    event_type: str
    n_results: int = 5


@router.post("/search", response_model=SearchResponse)
def rag_search(req: SearchRequest):
    """
    Search dementia care guidelines by natural language query.
    Returns relevant protocol excerpts with source citations.
    
    ⚠️ Only retrieves from authoritative sources. No generated advice.
    """
    results = search_protocols(
        query=req.query,
        n_results=req.n_results,
        source_filter=req.source_filter,
    )
    return SearchResponse(
        query=req.query,
        results=[ProtocolResult(**r) for r in results],
        count=len(results),
    )


@router.post("/event", response_model=SearchResponse)
def rag_event_search(req: EventSearchRequest):
    """
    Search protocols by behavioral event type.
    Supported types: agitation, sundowning, wandering, refusal, 
    fall, aggression, confusion, sleep_disturbance
    """
    results = search_by_event_type(
        event_type=req.event_type,
        n_results=req.n_results,
    )
    return SearchResponse(
        query=f"event_type:{req.event_type}",
        results=[ProtocolResult(**r) for r in results],
        count=len(results),
    )


@router.get("/sources")
def list_sources():
    """List all available guideline sources in the knowledge base."""
    return {
        "sources": [
            {"id": "CMS", "description": "CMS State Operations Manual, GUIDE Model, F-Tags"},
            {"id": "NICE", "description": "NICE NG97 Dementia Guidelines"},
            {"id": "APA", "description": "APA Guidelines for Evaluation of Dementia"},
            {"id": "Alzheimer's Association", "description": "Care Practice Recommendations & Clinical Guidelines"},
        ],
        "total_chunks": 2301,
        "event_types": [
            "agitation", "sundowning", "wandering", "refusal",
            "fall", "aggression", "confusion", "sleep_disturbance",
        ],
    }
