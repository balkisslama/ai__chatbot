from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, index, search, chat
from app.config import settings

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(index.router, prefix="/api/v1", tags=["Index"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

@app.get("/")
async def root():
    return {
        "message": "AI Chatbot API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}