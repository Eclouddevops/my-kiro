def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_list_project(client):
    r = client.post("/api/projects", json={"name": "My App"})
    assert r.status_code == 201
    pid = r.json()["id"]
    assert pid == "my-app"

    r = client.get("/api/projects")
    assert any(p["id"] == pid for p in r.json())


def test_write_read_tree(client):
    pid = client.post("/api/projects", json={"name": "demo"}).json()["id"]

    r = client.put(
        f"/api/projects/{pid}/files",
        json={"path": "src/app.py", "content": "x = 1\n"},
    )
    assert r.status_code == 200

    r = client.get(f"/api/projects/{pid}/files", params={"path": "src/app.py"})
    assert r.json()["content"] == "x = 1\n"

    r = client.get(f"/api/projects/{pid}/tree")
    paths = [n["path"] for n in r.json()]
    assert "src/app.py" in paths


def test_path_traversal_rejected(client):
    pid = client.post("/api/projects", json={"name": "demo"}).json()["id"]
    r = client.put(
        f"/api/projects/{pid}/files",
        json={"path": "../escape.py", "content": "bad"},
    )
    assert r.status_code == 400


def test_chat_returns_reply_and_proposals(client):
    pid = client.post("/api/projects", json={"name": "chatapp"}).json()["id"]
    r = client.post(
        f"/api/projects/{pid}/chat",
        json={"message": "make a hello world", "open_files": {}},
    )
    assert r.status_code == 200
    body = r.json()
    assert "starter file" in body["reply"]
    assert body["proposals"][0]["path"] == "main.py"


def test_apply_proposals_writes_files(client):
    pid = client.post("/api/projects", json={"name": "applyapp"}).json()["id"]
    chat = client.post(
        f"/api/projects/{pid}/chat",
        json={"message": "make it", "open_files": {}},
    ).json()

    r = client.post(
        f"/api/projects/{pid}/chat/apply",
        json={"proposals": chat["proposals"]},
    )
    assert r.status_code == 200
    assert "main.py" in r.json()

    read = client.get(f"/api/projects/{pid}/files", params={"path": "main.py"})
    assert "hello" in read.json()["content"]


def test_chat_404_for_missing_project(client):
    r = client.post(
        "/api/projects/nope/chat", json={"message": "hi", "open_files": {}}
    )
    assert r.status_code == 404
