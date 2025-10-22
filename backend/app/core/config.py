"""
Configuration settings for Africa Strategy API
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost/africa_strategy",
        env="DATABASE_URL"
    )

    # OpenRouter API Configuration
    OPENROUTER_API_KEY: str = Field(default="", env="OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # AI Models
    GEMINI_MODEL: str = "google/gemini-2.0-flash-exp:free"  # Gemini 2.5 Flash
    PERPLEXITY_MODEL: str = "perplexity/llama-3.1-sonar-large-128k-online"  # With internet access

    # Redis Configuration (optional)
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")

    # CORS Configuration
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
