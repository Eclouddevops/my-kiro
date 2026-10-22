import pytest

from app.config import Settings
from app.services.bedrock import BedrockError, BedrockService


class FakeClient:
    def __init__(self, text: str, raise_exc: Exception | None = None):
        self._text = text
        self._raise = raise_exc
        self.calls: list[dict] = []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        if self._raise:
            raise self._raise
        return {
            "output": {"message": {"content": [{"text": self._text}]}}
        }


def make_service(text: str, exc=None) -> tuple[BedrockService, FakeClient]:
    client = FakeClient(text, exc)
    svc = BedrockService(Settings(), client=client)
    return svc, client


def test_converse_extracts_text():
    svc, _ = make_service("Hello there")
    result = svc.converse([{"role": "user", "content": "hi"}])
    assert result.text == "Hello there"
    assert result.proposals == []


def test_converse_parses_proposals():
    text = (
        "Here is the file.\n"
        '```json\n{"operations": [{"path": "app.py", "action": "write", '
        '"content": "print(1)"}]}\n```'
    )
    svc, _ = make_service(text)
    result = svc.converse([{"role": "user", "content": "make app.py"}])
    assert len(result.proposals) == 1
    p = result.proposals[0]
    assert p.path == "app.py"
    assert p.action == "write"
    assert p.content == "print(1)"


def test_converse_ignores_bad_json_block():
    svc, _ = make_service("```json\n{not valid}\n```")
    result = svc.converse([{"role": "user", "content": "x"}])
    assert result.proposals == []


def test_converse_sanitizes_errors():
    from botocore.exceptions import BotoCoreError

    svc, _ = make_service("", exc=BotoCoreError())
    with pytest.raises(BedrockError) as ei:
        svc.converse([{"role": "user", "content": "x"}])
    # The raised message must not leak internal detail.
    assert "temporarily unavailable" in str(ei.value)


def test_messages_shaped_for_bedrock():
    svc, client = make_service("ok")
    svc.converse([{"role": "user", "content": "hi"}])
    sent = client.calls[0]["messages"]
    assert sent == [{"role": "user", "content": [{"text": "hi"}]}]
