"""
Configuration settings for Africa Strategy API
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

# Trouver le répertoire racine du projet (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./africa_strategy.db",  # SQLite par défaut (pas de dépendance)
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=5, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    
    # Debug Mode
    DEBUG: bool = Field(default=False, env="DEBUG")

    # OpenRouter API Configuration
    OPENROUTER_API_KEY: str = Field(default="", env="OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # OpenAI Assistants Configuration
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_ASSISTANT_ID: str = Field(default="", env="OPENAI_ASSISTANT_ID")

    # Pinecone Configuration
    PINECONE_API_KEY: str = Field(default="", env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = Field(default="us-east-1", env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = Field(default="africa-strategy-rag", env="PINECONE_INDEX_NAME")

    # AI Models
    GEMINI_MODEL: str = "google/gemini-2.0-flash-exp:free"  # Gemini 2.5 Flash
    PERPLEXITY_MODEL: str = "perplexity/llama-3.1-sonar-large-128k-online"  # With internet access

    # Redis Configuration (optional)
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")

    # CORS Configuration
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: list = ["*"]  # For development, restrict in production
    ENVIRONMENT: str = Field(default="development", env="APP_ENV")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Sentry (optional)
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignorer les variables supplémentaires dans .env


# Global settings instance
settings = Settings()

# Debug: Afficher les valeurs chargées (sans exposer la clé complète)
if settings.OPENAI_API_KEY:
    logger = __import__("logging").getLogger(__name__)
    logger.info(f"✅ OpenAI API Key chargée: {settings.OPENAI_API_KEY[:20]}...")
    logger.info(f"✅ OpenAI Assistant ID: {settings.OPENAI_ASSISTANT_ID}")
else:
    logger = __import__("logging").getLogger(__name__)
    logger.warning(f"⚠️ OpenAI API Key NON configurée !")
    logger.warning(f"   Fichier .env cherché: {ENV_FILE}")
    logger.warning(f"   Fichier existe: {ENV_FILE.exists()}")
