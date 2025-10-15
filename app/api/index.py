#After you upload a file, this code processes it in the background, 
# breaks it into searchable pieces, and prepares it so the chatbot 
#can find relevant information when you ask questions

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.file_processor import FileProcessor
from app.utils.text_utils import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.keyword_search import KeywordSearchService
from app.models.schemas import DocumentStatus
from typing import Dict
import os

router = APIRouter()

file_processor = FileProcessor()
text_chunker = TextChunker()
embedding_service = EmbeddingService()
vector_store = VectorStore()
keyword_search = KeywordSearchService()

# In-memory status tracking (use database in production)
processing_status = {}

def process_document_task(document_id: str, file_path: str, 
                         file_type: str, workspace_id: str, filename: str):
    """Background task to process document"""
    
    try:
        processing_status[document_id] = DocumentStatus.PROCESSING
        
        # Step 1: Extract content
        processed = file_processor.process_file(
            file_path=file_path,
            file_type=file_type,
            doc_id=document_id,
            filename=filename
        )
        
        content = processed['content']
        metadata = processed['metadata']
        
        # Step 2: Chunk text
        chunks = text_chunker.chunk_text(content, document_id)
        
        # Add metadata to chunks
        for chunk in chunks:
            chunk['metadata'] = metadata
        
        # Step 3: Generate embeddings
        chunk_texts = [chunk['content'] for chunk in chunks]
        embeddings = embedding_service.embed_batch(chunk_texts)
        
        # Step 4: Store in vector database
        vector_store.add_chunks(workspace_id, chunks, embeddings)
        
        # Step 5: Index for keyword search
        keyword_search.index_chunks(chunks, workspace_id)
        
        processing_status[document_id] = DocumentStatus.COMPLETED
        
    except Exception as e:
        processing_status[document_id] = DocumentStatus.FAILED
        print(f"Error processing {document_id}: {str(e)}")

@router.post("/index/{document_id}")
async def index_document(
    document_id: str,
    workspace_id: str,
    background_tasks: BackgroundTasks
):
    """Trigger document indexing"""
    
    # Find the uploaded file
    workspace_dir = os.path.join("uploads", workspace_id)
    files = [f for f in os.listdir(workspace_dir) if f.startswith(document_id)]
    
    if not files:
        raise HTTPException(404, "Document not found")
    
    file_path = os.path.join(workspace_dir, files[0])
    filename = files[0].split('_', 1)[1]  # Remove doc_id prefix
    
    # Detect file type from extension
    ext = filename.split('.')[-1].lower()
    file_type = ext
    
    # Add to background tasks
    background_tasks.add_task(
        process_document_task,
        document_id=document_id,
        file_path=file_path,
        file_type=file_type,
        workspace_id=workspace_id,
        filename=filename
    )
    
    return {
        "document_id": document_id,
        "status": "processing",
        "message": "Document indexing started"
    }

@router.get("/status/{document_id}")
async def get_status(document_id: str):
    """Check document processing status"""
    
    status = processing_status.get(document_id, DocumentStatus.PENDING)
    
    return {
        "document_id": document_id,
        "status": status
    }