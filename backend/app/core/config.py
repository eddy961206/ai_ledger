from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ai_household_ledger")
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # External APIs
    woori_bank_api_key: Optional[str] = os.getenv("WOORI_BANK_API_KEY")
    google_places_api_key: Optional[str] = os.getenv("GOOGLE_PLACES_API_KEY")
    google_gemini_api_key: Optional[str] = os.getenv("GOOGLE_GEMINI_API_KEY")
    
    # Ollama
    default_ollama_server_url: str = os.getenv("DEFAULT_OLLAMA_SERVER_URL", "http://localhost:11434")
    
    # CORS
    allowed_origins: list = ["*"]  # In production, specify exact origins
    
    class Config:
        env_file = ".env"

settings = Settings()

