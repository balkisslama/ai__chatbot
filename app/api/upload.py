#This endpoint successfully uploads a file, 
#saves it with a unique name, and returns information about the upload!

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import UploadResponse, FileType, DocumentStatus
import os
import uuid
from datetime import datetime
import magic

router = APIRouter()

def detect_file_type(content: bytes, filename: str) -> str:
    """Detect file type"""
    mime = magic.from_buffer(content, mime=True)
    ext = filename.split('.')[-1].lower()
    
    if 'pdf' in mime or ext == 'pdf':
        return 'pdf'
    elif 'image' in mime or ext in ['png', 'jpg', 'jpeg']:
        return 'image'
    elif ext == 'txt':
        return 'text'
    else:
        return ext

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), workspace_id: str = "default"):
    """Upload a file"""
    
    content = await file.read()
    file_size = len(content)
    
    file_type = detect_file_type(content, file.filename)
    doc_id = str(uuid.uuid4())
    
    workspace_dir = os.path.join("uploads", workspace_id)
    os.makedirs(workspace_dir, exist_ok=True)
    
    file_path = os.path.join(workspace_dir, f"{doc_id}_{file.filename}")
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    return UploadResponse(
        document_id=doc_id,
        filename=file.filename,
        file_type=file_type,
        size=file_size,
        status=DocumentStatus.PENDING,
        uploaded_at=datetime.now()
    )