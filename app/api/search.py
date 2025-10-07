
#This is the search engine that finds the most 
# relevant pieces of your documents when you ask a question, 
#using both AI understanding and keyword matching.

from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest, SearchResult
from app.services.retrieval_service import RetrievalService
from typing import List

router = APIRouter()
retrieval_service = RetrievalService()

@router.post("/search", response_model=List[SearchResult])
async def search(request: SearchRequest, workspace_id: str = "default"):
    """Search for relevant chunks"""
    
    try:
        results = retrieval_service.hybrid_search(
            query=request.query,
            workspace_id=workspace_id,
            top_k=request.top_k,
            filters=request.filters,
            use_semantic=request.use_semantic,
            use_keyword=request.use_keyword,
            semantic_weight=request.semantic_weight
        )
        
        return [
            SearchResult(
                chunk_id=r['chunk_id'],
                document_id=r['metadata']['document_id'],
                content=r['content'],
                score=r['score'],
                metadata=r['metadata']
            )
            for r in results
        ]
        
    except Exception as e:
        raise HTTPException(500, f"Search failed: {str(e)}")