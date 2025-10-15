from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from datetime import datetime

app = FastAPI(title="AI Chatbot API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs("uploads/default", exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "AI Chatbot API", 
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...), workspace_id: str = "default"):
    """Simple upload endpoint"""
    try:
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Read file
        content = await file.read()
        file_size = len(content)
        
        # Create workspace directory
        workspace_dir = os.path.join("uploads", workspace_id)
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(workspace_dir, f"{doc_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)
        
        return {
            "document_id": doc_id,
            "filename": file.filename,
            "file_type": file.filename.split('.')[-1],
            "size": file_size,
            "status": "uploaded",
            "uploaded_at": datetime.now().isoformat(),
            "message": "File uploaded successfully!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/health")
async def health():
    return {"status": "healthy"}