import os
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise SEO Engine"
    API_V1_STR: str = "/api/v1"
    
    # DB
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "seo_engine"
    DB_HOST: str = "db"
    DB_PORT: str = "5432"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Paths
    DATA_DIR: str = "/app/data"
    BASELINE_DIR: str = "/app/data/baseline"
    COMPETITOR_DIR: str = "/app/data/competitors"

    
    # Crawler
    MAX_CRAWL_DEPTH: int = 10
    MAX_PAGES: int = 1000  # Increased limit for full site crawl
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    
    # AI Analysis
    GROQ_API_KEY: Optional[str] = None
    
    # LangSmith Tracing
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "seo-compare-engine"
    
    DEBUG: bool = False

    model_config = ConfigDict(extra="ignore", env_file=".env")



settings = Settings()
