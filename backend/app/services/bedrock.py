"""Amazon Bedrock integration (R5).

Wraps the ``bedrock-runtime`` ``converse`` API. The service is the ONLY place
LLM calls happen; credentials come from the standard AWS provider chain on the
backend and never reach the client. Errors are sanitized before they propagate.

The assistant is instructed to optionally return a fenced ```json``` block
describing proposed file operations. We parse that block into structured
proposals that the client reviews and approves before anything is written
(R-SEC5).
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import Settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert pair-programming assistant embedded in a web IDE. "
    "Help the user design and build applications. When you want to create or "
    "modify files, include exactly one fenced code block tagged `json` with "
    "this shape:\n"
    '{"operations": [{"path": "relative/path.ext", "action": "write", '
    '"content": "<file content>"}]}\n'
    "Use project-relative POSIX paths only. Never use absolute paths or `..`. "
    "Explain your reasoning in prose outside the JSON block."
)

_JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


@dataclass
class FileProposal:
    path: str
    action: str  # "write" | "delete"
    content: str | None = None


@dataclass
class ChatResult:
    text: str
    proposals: list[FileProposal] = field(default_factory=list)


class BedrockError(RuntimeError):
    """Sanitized error raised when a Bedrock call fails."""


class BedrockService:
    def __init__(self, settings: Settings, client=None) -> None:
        self._settings = settings
        # Allow injection of a fake client in tests.
        self._client = client or boto3.client(
            "bedrock-runtime", region_name=settings.aws_region
        )

    def converse(self, messages: list[dict], system: str | None = None) -> ChatResult:
        """Call Bedrock with a list of {role, content} messages.

        ``messages`` roles are "user"/"assistant"; content is plain text.
        """
        bedrock_messages = [
            {"role": m["role"], "content": [{"text": m["content"]}]}
            for m in messages
        ]
        try:
            resp = self._client.converse(
                modelId=self._settings.bedrock_model_id,
                messages=bedrock_messages,
                system=[{"text": system or SYSTEM_PROMPT}],
                inferenceConfig={"maxTokens": 2048, "temperature": 0.2},
            )
        except (ClientError, BotoCoreError) as exc:
            # Log full detail server-side; return a generic message to the client.
            logger.exception("Bedrock converse failed")
            raise BedrockError("The AI service is temporarily unavailable.") from exc

        text = self._extract_text(resp)
        proposals = self._parse_proposals(text)
        return ChatResult(text=text, proposals=proposals)

    @staticmethod
    def _extract_text(resp: dict) -> str:
        try:
            parts = resp["output"]["message"]["content"]
            return "".join(p.get("text", "") for p in parts)
        except (KeyError, TypeError):
            return ""

    @staticmethod
    def _parse_proposals(text: str) -> list[FileProposal]:
        proposals: list[FileProposal] = []
        match = _JSON_BLOCK_RE.search(text)
        if not match:
            return proposals
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            logger.warning("Could not parse proposal JSON block")
            return proposals
        for op in data.get("operations", []):
            if not isinstance(op, dict) or "path" not in op:
                continue
            proposals.append(
                FileProposal(
                    path=str(op["path"]),
                    action=str(op.get("action", "write")),
                    content=op.get("content"),
                )
            )
        return proposals
