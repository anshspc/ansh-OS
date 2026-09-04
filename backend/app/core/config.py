import os
from typing import List, Union

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================================
    # Application
    # ==========================================
    ENVIRONMENT: str = "development"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # ==========================================
    # CORS
    # ==========================================
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "https://ansh-os-frontend.onrender.com",
        "https://ansh-os.onrender.com",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(
        cls,
        v: Union[str, List[str]],
    ) -> List[str]:
        standard_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "https://ansh-os-frontend.onrender.com",
            "https://ansh-os.onrender.com",
        ]

        if isinstance(v, str):
            if not v.strip():
                return standard_origins
            if not v.startswith("["):
                origins = [origin.strip() for origin in v.split(",") if origin.strip()]
                for origin in standard_origins:
                    if origin not in origins:
                        origins.append(origin)
                return origins

        if isinstance(v, list):
            origins = list(v)
            for origin in standard_origins:
                if origin not in origins:
                    origins.append(origin)
            return origins

        return standard_origins

    # ==========================================
    # Database
    # ==========================================
    DATABASE_URL: str = "sqlite+aiosqlite:///./personalix.db"

    @field_validator("DATABASE_URL", mode="before")
    def assemble_database_url(cls, v: str) -> str:
        if not v:
            return "sqlite+aiosqlite:///./personalix.db"
        # Render / standard PostgreSQL URL normalization for asyncpg
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        # asyncpg does not accept ?sslmode=, it uses ?ssl=
        if "sslmode=require" in v:
            v = v.replace("sslmode=require", "ssl=require")
        elif "sslmode=prefer" in v:
            v = v.replace("sslmode=prefer", "ssl=prefer")
        elif "sslmode=disable" in v:
            v = v.replace("sslmode=disable", "ssl=disable")
        return v

    # ==========================================
    # Redis
    # ==========================================
    REDIS_URL: str = "redis://localhost:6379/0"

    # ==========================================
    # Security & Authentication
    # ==========================================
    JWT_SECRET: str = "personalix-super-secure-production-ready-jwt-secret-key-32chars"
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==========================================
    # AI Configuration
    # ==========================================
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    DEFAULT_AI_PROVIDER: str = "auto"

    # ==========================================
    # RAG / Embeddings
    # ==========================================
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # ==========================================
    # File Storage
    # ==========================================
    UPLOAD_DIR: str = "./uploads"

    # ==========================================
    # Production Security Validation
    # ==========================================
    @model_validator(mode="after")
    def validate_security(self):
        # Ensure JWT_SECRET is never empty
        if not self.JWT_SECRET:
            self.JWT_SECRET = "personalix-super-secure-production-ready-jwt-secret-key-32chars"
        return self

    # ==========================================
    # Pydantic Settings Configuration
    # ==========================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()