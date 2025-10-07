from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, index, chat

app = FastAPI(
    title="AI Chatbot API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including routers
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(index.router, prefix="/api/v1", tags=["Index"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

@app.get("/")
async def root():
    return {
        "message": "AI Chatbot API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}