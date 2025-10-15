from app.services.vector_store import VectorStore
from app.services.keyword_search import KeywordSearchService
from app.services.embedding_service import EmbeddingService
from typing import List, Dict, Optional
from app.config import settings

class RetrievalService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.keyword_search = KeywordSearchService()
        self.embedding_service = EmbeddingService()
    
    def hybrid_search(self, query: str, workspace_id: str,
                     top_k: int = None, filters: Optional[Dict] = None,
                     use_semantic: bool = True, use_keyword: bool = True,
                     semantic_weight: float = 0.7) -> List[Dict]:
        """Hybrid search combining semantic and keyword search"""
        
        top_k = top_k or settings.TOP_K
        results = []
        
        # Semantic search
        if use_semantic:
            query_embedding = self.embedding_service.embed_text(query)
            semantic_results = self.vector_store.search(
                workspace_id=workspace_id,
                query_embedding=query_embedding,
                top_k=top_k * 2,  # Get more for fusion
                filters=filters
            )
            results.append(('semantic', semantic_results))
        
        # Keyword search
        if use_keyword:
            keyword_results = self.keyword_search.search(
                query=query,
                workspace_id=workspace_id,
                top_k=top_k * 2,
                filters=filters
            )
            results.append(('keyword', keyword_results))
        
        # Fusion
        if len(results) == 2:
            fused = self._reciprocal_rank_fusion(
                results,
                semantic_weight=semantic_weight,
                keyword_weight=1 - semantic_weight
            )
        elif len(results) == 1:
            fused = results[0][1]
        else:
            return []
        
        # Return top K
        return fused[:top_k]
    
    def _reciprocal_rank_fusion(self, results_list: List[tuple],
                                semantic_weight: float = 0.7,
                                keyword_weight: float = 0.3,
                                k: int = 60) -> List[Dict]:
        """Combine results using Reciprocal Rank Fusion"""
        
        # Calculate RRF scores
        chunk_scores = {}
        
        for search_type, results in results_list:
            weight = semantic_weight if search_type == 'semantic' else keyword_weight
            
            for rank, result in enumerate(results, 1):
                chunk_id = result['chunk_id']
                rrf_score = weight * (1 / (k + rank))
                
                if chunk_id in chunk_scores:
                    chunk_scores[chunk_id]['score'] += rrf_score
                else:
                    chunk_scores[chunk_id] = {
                        **result,
                        'score': rrf_score
                    }
        
        # Sort by combined score
        sorted_results = sorted(
            chunk_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return sorted_results