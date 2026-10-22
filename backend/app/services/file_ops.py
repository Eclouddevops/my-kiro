"""Filesystem-backed project store with validated file operations.

For the MVP, projects live on local disk under ``PROJECTS_DIR``. All reads and
writes go through path validation (see security.validation) so a project can
never read or write outside its own root — the core of R-SEC4.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from app.security.validation import ValidationError, validate_file_op


@dataclass(frozen=True)
class FileNode:
    path: str          # project-relative POSIX path
    is_dir: bool
    size: int = 0


class ProjectStore:
    """Manages project working directories on local disk."""

    def __init__(self, root: str) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def project_dir(self, project_id: str) -> Path:
        # project_id is validated as a safe slug by the caller/schema.
        d = (self.root / project_id).resolve()
        if not str(d).startswith(str(self.root)):
            raise ValidationError("project id escapes storage root")
        return d

    def create_project(self, project_id: str) -> Path:
        d = self.project_dir(project_id)
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _abs(self, project_id: str, rel: str) -> Path:
        base = self.project_dir(project_id)
        target = (base / rel).resolve()
        # Defense in depth: the resolved path must stay within the project dir.
        if not str(target).startswith(str(base)):
            raise ValidationError("resolved path escapes project root")
        return target

    def write_file(self, project_id: str, path: str, content: str) -> str:
        rel = validate_file_op(path, content)
        target = self._abs(project_id, rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return rel

    def read_file(self, project_id: str, path: str) -> str:
        rel = validate_file_op(path)
        target = self._abs(project_id, rel)
        if not target.is_file():
            raise FileNotFoundError(rel)
        return target.read_text(encoding="utf-8")

    def delete_file(self, project_id: str, path: str) -> str:
        rel = validate_file_op(path)
        target = self._abs(project_id, rel)
        if target.is_file():
            target.unlink()
        return rel

    def list_tree(self, project_id: str) -> list[FileNode]:
        base = self.project_dir(project_id)
        if not base.exists():
            return []
        nodes: list[FileNode] = []
        for dirpath, dirnames, filenames in os.walk(base):
            # Skip VCS internals in the tree view.
            dirnames[:] = [d for d in dirnames if d != ".git"]
            for name in sorted(dirnames):
                abs_dir = Path(dirpath) / name
                rel = abs_dir.relative_to(base).as_posix()
                nodes.append(FileNode(path=rel, is_dir=True))
            for name in sorted(filenames):
                abs_file = Path(dirpath) / name
                rel = abs_file.relative_to(base).as_posix()
                nodes.append(
                    FileNode(path=rel, is_dir=False, size=abs_file.stat().st_size)
                )
        return sorted(nodes, key=lambda n: (n.path.count("/"), n.path))
