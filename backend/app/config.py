"""
Application configuration management.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/healthcare_auditor"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    NEO4J_DATABASE: str = "neo4j"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    PROJECT_NAME: str = "Healthcare Auditor API"
    VERSION: str = "0.1.0"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Fraud Detection
    FRAUD_SCORE_THRESHOLD: float = 0.65
    ALERT_PRIORITY_HIGH: float = 0.95
    ALERT_PRIORITY_MEDIUM: float = 0.80
    ALERT_PRIORITY_LOW: float = 0.65
    
    # Knowledge Graph
    KG_CACHE_TTL_SECONDS: int = 3600
    MAX_RELATIONSHIP_DEPTH: int = 5
    
    # Data Ingestion
    INGEST_BATCH_SIZE: int = 1000
    INGEST_MAX_WORKERS: int = 4
    CODE_UPDATE_CHECK_INTERVAL_HOURS: int = 24
    
    # External APIs
    CMS_API_KEY: str = ""
    AMA_CPT_API_KEY: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
