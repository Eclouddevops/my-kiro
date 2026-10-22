import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.deps import get_bedrock, get_store
from app.main import create_app
from app.services.bedrock import BedrockService
from app.services.file_ops import ProjectStore


class FakeBedrockClient:
    """Returns a canned reply containing one file proposal."""

    def converse(self, **kwargs):
        text = (
            "I'll create a starter file.\n"
            '```json\n{"operations": [{"path": "main.py", "action": "write", '
            '"content": "print(\'hello\')"}]}\n```'
        )
        return {"output": {"message": {"content": [{"text": text}]}}}


@pytest.fixture
def client(tmp_path):
    settings = Settings(projects_dir=str(tmp_path / "_projects"))
    app = create_app(settings)

    store = ProjectStore(settings.projects_dir)
    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_bedrock] = lambda: BedrockService(
        settings, client=FakeBedrockClient()
    )

    with TestClient(app) as c:
        yield c
