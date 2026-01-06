"""
Application configuration settings.
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database - SQLite for local dev, PostgreSQL for Docker
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./online_exam.db"  # Default to SQLite for local development
    )
    
    # JWT Settings
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    app_name: str = "Online Sınav Sistemi"
    debug: bool = False
    testing: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
