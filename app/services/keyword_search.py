from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import And, Term
from typing import List, Dict, Optional
import os

class KeywordSearchService:
    def __init__(self, index_dir: str = "./whoosh_index"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        
        self.schema = Schema(
            chunk_id=ID(stored=True, unique=True),
            document_id=ID(stored=True),
            content=TEXT(stored=True),
            workspace_id=ID(stored=True),
            language=KEYWORD(stored=True),
            tags=KEYWORD(stored=True, commas=True)
        )
    
    def get_or_create_index(self):
        """Get existing index or create new one"""
        if exists_in(self.index_dir, indexname="chunks"):
            return open_dir(self.index_dir, indexname="chunks")
        else:
            return create_in(self.index_dir, self.schema, indexname="chunks")
    
    def index_chunks(self, chunks: List[Dict], workspace_id: str):
        """Add chunks to keyword index"""
        ix = self.get_or_create_index()
        writer = ix.writer()
        
        for chunk in chunks:
            writer.add_document(
                chunk_id=chunk['chunk_id'],
                document_id=chunk['document_id'],
                content=chunk['content'],
                workspace_id=workspace_id,
                language=chunk.get('metadata', {}).get('language', ''),
                tags=','.join(chunk.get('metadata', {}).get('tags', []))
            )
        
        writer.commit()
    
    def search(self, query: str, workspace_id: str, top_k: int = 10,
               filters: Optional[Dict] = None) -> List[Dict]:
        """Search using keywords"""
        ix = self.get_or_create_index()
        
        with ix.searcher() as searcher:
            # Parse query
            parser = MultifieldParser(["content"], schema=ix.schema)
            parsed_query = parser.parse(query)
            
            # Add workspace filter
            workspace_filter = Term("workspace_id", workspace_id)
            final_query = And([parsed_query, workspace_filter])
            
            # Add additional filters
            if filters:
                for key, value in filters.items():
                    final_query = And([final_query, Term(key, str(value))])
            
            # Search
            results = searcher.search(final_query, limit=top_k)
            
            # Format results
            search_results = []
            for hit in results:
                search_results.append({
                    'chunk_id': hit['chunk_id'],
                    'document_id': hit['document_id'],
                    'content': hit['content'],
                    'score': hit.score,
                    'metadata': {
                        'language': hit.get('language'),
                        'tags': hit.get('tags', '').split(',') if hit.get('tags') else []
                    }
                })
            
            return search_results