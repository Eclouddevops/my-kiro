"""Validation for file paths and AI-generated file operations (R-SEC4).

All project file paths are resolved against the project root. We reject:
  - absolute paths
  - paths containing parent traversal that escape the root
  - disallowed extensions
  - files exceeding a maximum size

These checks apply equally to direct writes and to file operations proposed by
the LLM before they are applied.
"""
from __future__ import annotations

import re
from pathlib import PurePosixPath

MAX_FILE_BYTES = 1_000_000  # 1 MB per file

# Allow-list of extensions the editor/generator may write.
ALLOWED_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".txt",
        ".html", ".css", ".scss", ".yml", ".yaml", ".toml", ".ini",
        ".cfg", ".sh", ".env", ".sql", ".xml", ".svg", ".gitignore",
        ".dockerfile", "",  # "" allows extensionless files like Dockerfile
    }
)


class ValidationError(ValueError):
    """Raised when a path or file operation fails validation."""


def normalize_rel_path(raw: str) -> str:
    """Return a safe, normalized project-relative POSIX path.

    Raises ValidationError if the path is absolute, empty, or escapes the root.
    """
    if not raw or not raw.strip():
        raise ValidationError("empty path")

    # Normalize separators; project paths are always POSIX-style.
    candidate = raw.replace("\\", "/").strip()

    # Reject Windows drive-letter paths (e.g. "C:/x") and UNC-style roots.
    # PurePosixPath does not treat these as absolute, so check explicitly.
    if re.match(r"^[A-Za-z]:", candidate) or candidate.startswith("//"):
        raise ValidationError(f"absolute paths are not allowed: {raw!r}")

    p = PurePosixPath(candidate)
    if p.is_absolute():
        raise ValidationError(f"absolute paths are not allowed: {raw!r}")

    parts: list[str] = []
    for part in p.parts:
        if part in ("", "."):
            continue
        if part == "..":
            raise ValidationError(f"path traversal is not allowed: {raw!r}")
        parts.append(part)

    if not parts:
        raise ValidationError(f"path resolves to project root: {raw!r}")

    return "/".join(parts)


def validate_extension(rel_path: str) -> None:
    name = PurePosixPath(rel_path).name
    # Dotfiles like .gitignore: treat the whole name's suffix.
    suffix = PurePosixPath(name).suffix.lower()
    # Special-case common extensionless well-known files.
    if suffix == "" and name.lower() in {"dockerfile", "makefile", "procfile"}:
        return
    if suffix not in ALLOWED_EXTENSIONS and name.lower() not in {
        ".gitignore",
        ".dockerignore",
        ".env",
        ".env.example",
    }:
        raise ValidationError(f"extension not allowed: {name!r}")


def validate_size(content: str | bytes) -> None:
    size = len(content.encode("utf-8")) if isinstance(content, str) else len(content)
    if size > MAX_FILE_BYTES:
        raise ValidationError(
            f"file too large: {size} bytes (max {MAX_FILE_BYTES})"
        )


def validate_file_op(path: str, content: str | None = None) -> str:
    """Validate a single file operation and return the normalized path.

    Used for both direct writes and LLM-proposed operations.
    """
    rel = normalize_rel_path(path)
    validate_extension(rel)
    if content is not None:
        validate_size(content)
    return rel
