"""Application configuration using Pydantic settings"""
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # Application
    app_name: str = "AI Doctor Chatbot"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Security
    secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Database
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str
    database_url: Optional[str] = None

    @validator("database_url", pre=True, always=True)
    def assemble_db_url(cls, v, values):
        """Construct database URL if not provided"""
        if v:
            return v
        return (
            f"postgresql+asyncpg://{values['postgres_user']}:"
            f"{values['postgres_password']}@{values['postgres_host']}:"
            f"{values['postgres_port']}/{values['postgres_db']}"
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # Vector Database
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "medical_knowledge"

    # LLM APIs
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None

    # LLM Configuration
    primary_llm: str = "openai"
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2000
    embedding_model: str = "text-embedding-3-large"

    # External APIs
    weather_api_key: Optional[str] = None
    air_quality_api_key: Optional[str] = None

    # Monitoring
    sentry_dsn: Optional[str] = None
    prometheus_port: int = 9090

    # Safety
    enable_guardrails: bool = True
    emergency_alert_email: Optional[str] = None
    emergency_alert_phone: Optional[str] = None

    # RAG Settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_retrieval: int = 10
    rerank_top_k: int = 5
    hybrid_alpha: float = 0.5

    # Agent Settings
    max_agent_iterations: int = 10
    agent_timeout_seconds: int = 60

    # File Upload
    max_upload_size_mb: int = 10
    allowed_image_types: List[str] = ["jpg", "jpeg", "png", "pdf"]
    allowed_document_types: List[str] = ["pdf", "txt", "docx"]

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


# Global settings instance
settings = Settings()
