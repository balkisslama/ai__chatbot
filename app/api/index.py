#After you upload a file, this code processes it in the background, 
# breaks it into searchable pieces, and prepares it so the chatbot 
#can find relevant information when you ask questions

from fastapi import APIRouter, BackgroundTasks
from app.services.file_processor import FileProcessor
from app.utils.text_utils import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
import os

router = APIRouter()

file_processor = FileProcessor()
text_chunker = TextChunker()
embedding_service = EmbeddingService()
vector_store = VectorStore()

processing_status = {}

def process_document_task(document_id: str, file_path: str, file_type: str, workspace_id: str):
    """Background processing task"""
    try:
        processing_status[document_id] = "processing"
        
        # Extract text
        if file_type == 'pdf':
            text = file_processor.process_pdf(file_path)
        elif file_type == 'image':
            text = file_processor.process_image(file_path)
        elif file_type == 'text':
            text = file_processor.process_text(file_path)
        else:
            text = ""
        
        if not text:
            processing_status[document_id] = "failed"
            return
        
        # Chunk text
        chunks = text_chunker.chunk_text(text, document_id)
        
        # Generate embeddings
        chunk_texts = [chunk['content'] for chunk in chunks]
        embeddings = embedding_service.embed_batch(chunk_texts)
        
        # Store in vector DB
        vector_store.add_chunks(workspace_id, chunks, embeddings)
        
        processing_status[document_id] = "completed"
        
    except Exception as e:
        print(f"Processing error: {e}")
        processing_status[document_id] = "failed"

@router.post("/index/{document_id}")
async def index_document(document_id: str, workspace_id: str, background_tasks: BackgroundTasks):
    """Trigger document indexing"""
    
    workspace_dir = os.path.join("uploads", workspace_id)
    files = [f for f in os.listdir(workspace_dir) if f.startswith(document_id)]
    
    if not files:
        return {"error": "Document not found"}
    
    file_path = os.path.join(workspace_dir, files[0])
    filename = files[0].split('_', 1)[1]
    file_type = filename.split('.')[-1].lower()
    
    background_tasks.add_task(process_document_task, document_id, file_path, file_type, workspace_id)
    
    return {"document_id": document_id, "status": "processing"}

@router.get("/status/{document_id}")
async def get_status(document_id: str):
    """Get processing status"""
    status = processing_status.get(document_id, "pending")
    return {"document_id": document_id, "status": status}