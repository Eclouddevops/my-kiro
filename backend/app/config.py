"""Application configuration loaded from environment / .env.

All secrets (JWT, AWS) are read here and never sent to the frontend.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Database
    database_url: str = "postgresql+psycopg://ide:ide@localhost:5432/ide"

    # Storage
    storage_backend: str = "fs"  # fs | s3
    projects_dir: str = "./_projects"
    s3_bucket: str = ""
    s3_prefix: str = "projects/"

    # AWS / Bedrock
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    context_token_budget: int = 12000

    # Execution sandbox
    exec_image: str = "python:3.11-slim"
    exec_timeout_seconds: int = 30
    exec_memory_limit: str = "256m"
    exec_cpu_limit: float = 0.5
    exec_pids_limit: int = 128

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
