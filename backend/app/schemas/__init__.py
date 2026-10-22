"""Pydantic request/response schemas."""
from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class ProjectOut(BaseModel):
    id: str
    name: str


class FileNodeOut(BaseModel):
    path: str
    is_dir: bool
    size: int = 0


class FileWrite(BaseModel):
    path: str
    content: str


class FileOut(BaseModel):
    path: str
    content: str


class ChatMessageIn(BaseModel):
    message: str = Field(min_length=1)
    open_files: dict[str, str] = Field(default_factory=dict)


class ProposalOut(BaseModel):
    path: str
    action: str
    content: str | None = None


class ChatResponse(BaseModel):
    reply: str
    proposals: list[ProposalOut] = Field(default_factory=list)


class ApplyProposals(BaseModel):
    proposals: list[ProposalOut]


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    slug = slug[:63] or "project"
    if not _SLUG_RE.match(slug):
        slug = "project"
    return slug
