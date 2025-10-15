from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    CSV = "csv"
    EXCEL = "excel"
    DOCX = "docx"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: FileType
    size: int
    status: DocumentStatus
    uploaded_at: datetime

class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    file_type: FileType
    language: Optional[str] = None
    page_count: Optional[int] = None
    created_at: datetime
    tags: List[str] = []
    custom_metadata: Dict = {}

class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: Dict

class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict] = None
    top_k: int = 5
    use_semantic: bool = True
    use_keyword: bool = True
    semantic_weight: float = 0.7

class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: Dict

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    workspace_id: str
    filters: Optional[Dict] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[SearchResult]
    conversation_id: str