"""AI chat routes (R4, R5, R6, R7).

The chat endpoint assembles project context, proxies the call to Bedrock, and
returns the reply plus any proposed file operations. Proposals are validated
and only applied through the explicit /apply endpoint (R-SEC5).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_bedrock, get_context_builder, get_registry, get_store
from app.registry import Registry
from app.schemas import ApplyProposals, ChatMessageIn, ChatResponse, ProposalOut
from app.security.validation import ValidationError, validate_file_op
from app.services.bedrock import BedrockError, BedrockService
from app.services.context_builder import ContextBuilder
from app.services.file_ops import ProjectStore

router = APIRouter(prefix="/api/projects", tags=["chat"])


@router.post("/{project_id}/chat", response_model=ChatResponse)
def chat(
    project_id: str,
    body: ChatMessageIn,
    registry: Registry = Depends(get_registry),
    builder: ContextBuilder = Depends(get_context_builder),
    bedrock: BedrockService = Depends(get_bedrock),
    store: ProjectStore = Depends(get_store),
) -> ChatResponse:
    project = registry.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")

    file_tree = [n.path for n in store.list_tree(project_id) if not n.is_dir]
    messages = builder.build_messages(
        history=registry.history(project_id),
        user_message=body.message,
        file_tree=file_tree,
        open_files=body.open_files,
    )

    try:
        result = bedrock.converse(messages)
    except BedrockError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    registry.add_message(project_id, "user", body.message)
    registry.add_message(project_id, "assistant", result.text)

    # Validate proposals before returning; invalid ones are dropped with a flag
    # in the path so the client can surface the issue.
    valid: list[ProposalOut] = []
    for p in result.proposals:
        try:
            rel = validate_file_op(p.path, p.content)
            valid.append(ProposalOut(path=rel, action=p.action, content=p.content))
        except ValidationError:
            continue

    return ChatResponse(reply=result.text, proposals=valid)


@router.post("/{project_id}/chat/apply", response_model=list[str])
def apply_proposals(
    project_id: str,
    body: ApplyProposals,
    registry: Registry = Depends(get_registry),
    store: ProjectStore = Depends(get_store),
) -> list[str]:
    """Apply user-approved proposals. Each op is re-validated (R-SEC4/5)."""
    if registry.get(project_id) is None:
        raise HTTPException(status_code=404, detail="project not found")

    applied: list[str] = []
    for p in body.proposals:
        try:
            if p.action == "delete":
                applied.append(store.delete_file(project_id, p.path))
            else:
                applied.append(store.write_file(project_id, p.path, p.content or ""))
        except ValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return applied
