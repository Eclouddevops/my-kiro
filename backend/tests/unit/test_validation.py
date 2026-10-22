import pytest

from app.security.validation import (
    ValidationError,
    normalize_rel_path,
    validate_extension,
    validate_file_op,
    validate_size,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("src/app.py", "src/app.py"),
        ("./src/./app.py", "src/app.py"),
        ("src\\win\\path.ts", "src/win/path.ts"),
        ("README.md", "README.md"),
    ],
)
def test_normalize_ok(raw, expected):
    assert normalize_rel_path(raw) == expected


@pytest.mark.parametrize(
    "raw",
    ["", "   ", "/etc/passwd", "../secret", "src/../../etc", "C:/abs"],
)
def test_normalize_rejects_bad_paths(raw):
    with pytest.raises(ValidationError):
        normalize_rel_path(raw)


def test_extension_allow_list():
    validate_extension("a/b/c.py")
    validate_extension("Dockerfile")
    validate_extension(".gitignore")
    with pytest.raises(ValidationError):
        validate_extension("evil.exe")


def test_size_limit():
    validate_size("x" * 10)
    with pytest.raises(ValidationError):
        validate_size("x" * 2_000_000)


def test_validate_file_op_returns_normalized():
    assert validate_file_op("./src/app.py", "print('hi')") == "src/app.py"
    with pytest.raises(ValidationError):
        validate_file_op("../escape.py", "x")
