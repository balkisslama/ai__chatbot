from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "AI Chatbot API"
    API_VERSION: str = "1.0.0"
    
    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    TEMP_DIR: str = "temp_files"
    
    # Supported formats
    SUPPORTED_FORMATS: list = [
        "pdf", "png", "jpg", "jpeg", "txt",
        "csv", "xlsx", "xls", "docx"
    ]
    
    # OCR Settings
    TESSERACT_CONFIG: str = "--oem 3 --psm 6"
    OCR_LANGUAGES: str = "eng+fra+ara"  # English, French, Arabic
    
    # Chunking
    CHUNK_SIZE: int = 500  # tokens
    CHUNK_OVERLAP: int = 50  # tokens
    
    # Embedding
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Vector DB
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # LLM
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.7
    
    # Retrieval
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"

settings = Settings()