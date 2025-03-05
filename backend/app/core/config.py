import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "QA Database"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8080"]
    
    # Database
    SQLITE_DATABASE_URL: str = "sqlite:///./qa_database.db"
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "qa_database")
    
    # Use SQLite for development, PostgreSQL for production
    DATABASE_URL: str = os.getenv("DATABASE_URL", SQLITE_DATABASE_URL)
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    model_config = {
        "case_sensitive": True
    }


settings = Settings()
