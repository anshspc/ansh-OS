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
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls,
        v: Union[str, List[str]],
    ) -> List[str]:
        if isinstance(v, str):
            if not v.strip():
                return []

            if not v.startswith("["):
                return [
                    origin.strip()
                    for origin in v.split(",")
                    if origin.strip()
                ]

        if isinstance(v, list):
            return v

        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
        ]

    # ==========================================
    # Database
    # ==========================================
    DATABASE_URL: str = "sqlite+aiosqlite:///./personalix.db"

    # ==========================================
    # Redis
    # ==========================================
    REDIS_URL: str = "redis://localhost:6379/0"

    # ==========================================
    # Security & Authentication
    # ==========================================
    # MUST be supplied through .env in production.
    # Never commit the real value to Git.
    JWT_SECRET: str = ""

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
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
    def validate_production_security(self):
        environment = self.ENVIRONMENT.strip().lower()

        if environment == "production":
            # JWT secret must be explicitly configured.
            if not self.JWT_SECRET:
                raise ValueError(
                    "JWT_SECRET must be configured in production."
                )

            # Require a sufficiently strong secret.
            if len(self.JWT_SECRET) < 32:
                raise ValueError(
                    "JWT_SECRET must contain at least 32 characters in production."
                )

            # Wildcard CORS must never be used in production.
            if "*" in self.CORS_ORIGINS:
                raise ValueError(
                    "CORS_ORIGINS must not contain '*' in production."
                )

            # Production should have at least one explicitly allowed origin.
            if not self.CORS_ORIGINS:
                raise ValueError(
                    "CORS_ORIGINS must contain at least one allowed origin in production."
                )

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