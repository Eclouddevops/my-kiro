"""In-memory project + conversation registry for the MVP.

Phase 2 replaces this with PostgreSQL-backed models and migrations. The
interface is intentionally small so the swap is mechanical.
"""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field

from app.schemas import slugify


@dataclass
class Project:
    id: str
    name: str
    messages: list[dict] = field(default_factory=list)


class Registry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._projects: dict[str, Project] = {}

    def create_project(self, name: str) -> Project:
        with self._lock:
            base = slugify(name)
            pid = base
            # Ensure uniqueness without leaking a guessable-only id.
            if pid in self._projects:
                pid = f"{base}-{uuid.uuid4().hex[:6]}"
            project = Project(id=pid, name=name)
            self._projects[pid] = project
            return project

    def list_projects(self) -> list[Project]:
        with self._lock:
            return list(self._projects.values())

    def get(self, project_id: str) -> Project | None:
        with self._lock:
            return self._projects.get(project_id)

    def add_message(self, project_id: str, role: str, content: str) -> None:
        with self._lock:
            p = self._projects.get(project_id)
            if p is not None:
                p.messages.append({"role": role, "content": content})

    def history(self, project_id: str) -> list[dict]:
        with self._lock:
            p = self._projects.get(project_id)
            return list(p.messages) if p else []
