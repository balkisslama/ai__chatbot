import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from app.config import settings
import uuid

class VectorStore:
    def __init__(self):
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False
        ))
    
    def create_collection(self, workspace_id: str):
        """Create or get a collection for a workspace"""
        collection_name = f"workspace_{workspace_id}"
        
        try:
            collection = self.client.get_collection(collection_name)
        except:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"workspace_id": workspace_id}
            )
        
        return collection
    
    def add_chunks(self, workspace_id: str, chunks: List[Dict], 
                   embeddings: List[List[float]]):
        """Add chunks with embeddings to the collection"""
        collection = self.create_collection(workspace_id)
        
        ids = [chunk['chunk_id'] for chunk in chunks]
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [{
            'document_id': chunk['document_id'],
            'chunk_index': chunk['chunk_index'],
            **chunk.get('metadata', {})
        } for chunk in chunks]
        
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    def search(self, workspace_id: str, query_embedding: List[float],
               top_k: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """Semantic search using query embedding"""
        collection = self.create_collection(workspace_id)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters if filters else None
        )
        
        # Format results
        search_results = []
        for i in range(len(results['ids'][0])):
            search_results.append({
                'chunk_id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                'metadata': results['metadatas'][0][i]
            })
        
        return search_results
    
    def delete_document(self, workspace_id: str, document_id: str):
        """Delete all chunks for a document"""
        collection = self.create_collection(workspace_id)
        
        collection.delete(
            where={"document_id": document_id}
        )