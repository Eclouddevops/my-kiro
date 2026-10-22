"""Dependency-injection providers shared across routers.

For the MVP these are module-level singletons. Phase 2/4 introduce a DB session
and real authenticated-user resolution.
"""
from __future__ import annotations

from functools import lru_cache

from app.config import get_settings
from app.registry import Registry
from app.services.bedrock import BedrockService
from app.services.context_builder import ContextBuilder
from app.services.file_ops import ProjectStore

_registry = Registry()


def get_registry() -> Registry:
    return _registry


@lru_cache
def get_store() -> ProjectStore:
    settings = get_settings()
    return ProjectStore(settings.projects_dir)


@lru_cache
def get_context_builder() -> ContextBuilder:
    settings = get_settings()
    return ContextBuilder(token_budget=settings.context_token_budget)


def get_bedrock() -> BedrockService:
    return BedrockService(get_settings())
