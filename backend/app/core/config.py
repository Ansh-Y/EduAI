import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduAI — AI-Powered University Learning Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "eduai-super-secret-production-grade-jwt-key-2025-token")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # SQLite local database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./storage/eduai.db")
    
    # Groq API configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # File storage
    BASE_STORAGE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../storage"))
    NOTES_DIR: str = os.path.join(BASE_STORAGE_DIR, "notes")
    CERTIFICATES_DIR: str = os.path.join(BASE_STORAGE_DIR, "certificates")
    UPLOADS_DIR: str = os.path.join(BASE_STORAGE_DIR, "uploads")
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.NOTES_DIR, exist_ok=True)
os.makedirs(settings.CERTIFICATES_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
