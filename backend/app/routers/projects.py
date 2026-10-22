"""Project + file routes (R2, R6)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.deps import get_registry, get_store
from app.registry import Registry
from app.schemas import (
    FileNodeOut,
    FileOut,
    FileWrite,
    ProjectCreate,
    ProjectOut,
)
from app.security.validation import ValidationError
from app.services.file_ops import ProjectStore

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(registry: Registry = Depends(get_registry)) -> list[ProjectOut]:
    return [ProjectOut(id=p.id, name=p.name) for p in registry.list_projects()]


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    body: ProjectCreate,
    registry: Registry = Depends(get_registry),
    store: ProjectStore = Depends(get_store),
) -> ProjectOut:
    project = registry.create_project(body.name)
    store.create_project(project.id)
    return ProjectOut(id=project.id, name=project.name)


def _require_project(project_id: str, registry: Registry):
    project = registry.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return project


@router.get("/{project_id}/tree", response_model=list[FileNodeOut])
def tree(
    project_id: str,
    registry: Registry = Depends(get_registry),
    store: ProjectStore = Depends(get_store),
) -> list[FileNodeOut]:
    _require_project(project_id, registry)
    return [
        FileNodeOut(path=n.path, is_dir=n.is_dir, size=n.size)
        for n in store.list_tree(project_id)
    ]


@router.get("/{project_id}/files", response_model=FileOut)
def read_file(
    project_id: str,
    path: str = Query(...),
    registry: Registry = Depends(get_registry),
    store: ProjectStore = Depends(get_store),
) -> FileOut:
    _require_project(project_id, registry)
    try:
        content = store.read_file(project_id, path)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="file not found") from exc
    return FileOut(path=path, content=content)


@router.put("/{project_id}/files", response_model=FileOut)
def write_file(
    project_id: str,
    body: FileWrite,
    registry: Registry = Depends(get_registry),
    store: ProjectStore = Depends(get_store),
) -> FileOut:
    _require_project(project_id, registry)
    try:
        rel = store.write_file(project_id, body.path, body.content)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FileOut(path=rel, content=body.content)
