# Design & Architecture: AI-Powered IDE

## 1. System overview

```
┌───────────────────────────────────────────────────────────┐
│                        Browser (SPA)                        │
│  React + TypeScript + Vite                                  │
│  ┌──────────┬───────────────────────┬──────────────────┐   │
│  │ Sidebar  │   Monaco Editor        │   AI Chat Panel  │   │
│  │ (files / │   (tabs, highlight)    │   (messages,     │   │
│  │  git)    │                        │    proposals)    │   │
│  ├──────────┴───────────────────────┴──────────────────┤   │
│  │                 Terminal Panel (xterm.js)            │   │
│  └──────────────────────────────────────────────────────┘  │
└───────────────┬───────────────────────────────────────────┘
                │ HTTPS (JWT bearer)  +  WebSocket (terminal/stream)
                ▼
┌───────────────────────────────────────────────────────────┐
│                   Backend — FastAPI (Python)                │
│  Routers: auth, projects, files, chat, git, exec            │
│  Services: BedrockService, ProjectService, GitService,      │
│            ExecutorService, ContextBuilder                  │
│  Security: JWT auth, path validation, approval gating       │
└───────┬───────────────────┬───────────────┬───────────────┘
        │                   │               │
        ▼                   ▼               ▼
  Amazon Bedrock       PostgreSQL          S3
  (LLM, AWS SDK)    (users, projects,   (project artifacts,
                     messages, meta)     large files)
        │
        ▼
  Isolated executor (Docker container per run:
  non-root, resource limits, no network, timeout)
```

## 2. Technology choices

| Layer         | Choice                                   | Reason                          |
|---------------|------------------------------------------|---------------------------------|
| Frontend      | React 18 + TypeScript + Vite             | Fast DX, typed, modern tooling  |
| Editor        | `@monaco-editor/react`                   | VS Code-grade editing           |
| Terminal UI   | `xterm.js`                               | Standard web terminal           |
| State         | Zustand                                  | Lightweight, no boilerplate     |
| Backend       | FastAPI + Uvicorn                        | Async, typed, OpenAPI built-in  |
| ORM           | SQLAlchemy 2.x + Alembic                 | Mature, migrations              |
| DB            | PostgreSQL                               | Required by spec                |
| Object store  | S3 (boto3)                               | Required by spec                |
| LLM           | Amazon Bedrock (boto3 `bedrock-runtime`) | Required by spec                |
| Auth          | JWT (python-jose) + passlib[bcrypt]      | Stateless, standard             |
| Execution     | Docker SDK for Python                     | Per-run isolated containers     |
| Tests         | pytest (backend), Vitest + RTL (frontend)| Ecosystem standard              |

## 3. Backend module layout

```
backend/
  app/
    main.py                 # FastAPI app factory, CORS, router mounting
    config.py               # pydantic-settings; all secrets via env
    db.py                   # engine, session, Base
    deps.py                 # DI: get_db, get_current_user
    models/                 # SQLAlchemy models: user, project, file, message
    schemas/                # pydantic request/response models
    routers/
      auth.py               # register, login, me
      projects.py           # CRUD + access control
      files.py              # read/write/list; path validation
      chat.py               # LLM proxy; context assembly; proposals
      git.py                # status/diff/commit/branches
      exec.py               # run build/test in isolation (ws stream)
    services/
      bedrock.py            # BedrockService: converse() wrapper
      context_builder.py    # assemble project context within token budget
      file_ops.py           # validated file operations (R-SEC4)
      git_service.py        # GitPython wrapper
      executor.py           # Docker-based sandbox (R-SEC2/3)
    security/
      jwt.py                # token encode/decode
      validation.py         # path + file-op validation
  tests/
    unit/                   # service-level unit tests
    integration/            # API tests via httpx + test DB
  pyproject.toml
  Dockerfile
```

## 4. Key backend components

### 4.1 BedrockService

- Wraps `bedrock-runtime` `converse` API.
- Model id configurable via `BEDROCK_MODEL_ID`.
- Input: system prompt + message list + tool/response-format spec.
- Output: assistant text and a structured list of proposed file operations
  (JSON) parsed from a constrained response schema.
- Never returns credentials; errors are sanitized before reaching the client.

### 4.2 ContextBuilder

- Inputs: project id, current file tree, open/active files, last N messages.
- Produces a prompt payload within a configurable token budget
  (`CONTEXT_TOKEN_BUDGET`), truncating oldest/largest content first.

### 4.3 FileOps / validation (R-SEC4)

- All paths resolved against the project root; reject `..`, absolute paths,
  symlinks escaping root.
- Enforce allowed extensions and max file size.
- File operations from the LLM are returned as *proposals*; they are applied
  only after client confirmation (R-SEC5).

### 4.4 ExecutorService (R-SEC2/3)

- Runs build/test commands inside a short-lived Docker container:
  - non-root user, `--read-only` root fs with a writable project mount,
  - `--network none`, `--memory`, `--cpus`, `--pids-limit`,
  - hard timeout; container killed on expiry.
- Streams stdout/stderr to the terminal panel over WebSocket.

### 4.5 GitService

- GitPython-backed: `init`, `status`, `diff`, `add`, `commit`, `branch -l`.
- Scoped to the project working directory.

## 5. Data model (PostgreSQL)

```
users(id, email UNIQUE, password_hash, created_at)
projects(id, owner_id FK users, name, slug, created_at)
project_members(project_id FK, user_id FK, role)         # access control
files(id, project_id FK, path, size, updated_at)          # metadata; blob in S3/FS
messages(id, project_id FK, role, content, created_at)    # conversation history
```

- Project artifacts stored on local volume in dev; S3 in cloud
  (`STORAGE_BACKEND=fs|s3`).

## 6. API surface (REST unless noted)

| Method | Path                               | Purpose                        |
|--------|------------------------------------|--------------------------------|
| POST   | /api/auth/register                 | Create user                    |
| POST   | /api/auth/login                    | Obtain JWT                     |
| GET    | /api/auth/me                       | Current user                   |
| GET    | /api/projects                      | List accessible projects       |
| POST   | /api/projects                      | Create project                 |
| GET    | /api/projects/{id}/tree            | File tree                      |
| GET    | /api/projects/{id}/files           | Read file (?path=)             |
| PUT    | /api/projects/{id}/files           | Write file (validated)         |
| POST   | /api/projects/{id}/chat            | Chat; returns reply+proposals  |
| POST   | /api/projects/{id}/chat/apply      | Apply approved proposals       |
| GET    | /api/projects/{id}/git/status      | Git status                     |
| POST   | /api/projects/{id}/git/commit      | Stage+commit                   |
| WS     | /api/projects/{id}/exec            | Run build/test, stream output  |

All project-scoped routes enforce membership via `get_current_user` +
project access check.

## 7. Frontend structure

```
frontend/
  src/
    main.tsx, App.tsx
    layout/            # IDELayout, panels, resizers
    components/
      Sidebar/         # ProjectList, FileTree, SourceControl
      Editor/          # MonacoEditor wrapper, Tabs
      Chat/            # ChatPanel, Message, ProposalReview
      Terminal/        # TerminalPanel (xterm)
    store/             # zustand stores (project, editor, chat)
    api/               # typed fetch client + auth interceptor
    theme/             # dark theme tokens
  index.html
  vite.config.ts
  Dockerfile
```

## 8. Security design summary

- Secrets only on backend via env; CORS locked to known origins.
- JWT with short expiry; project access checked per request.
- File-op allow-list + path validation; LLM proposals require approval.
- Execution sandboxed with Docker: no network, resource caps, timeout,
  non-root. No host paths mounted except the single project dir (read/write).

## 9. Phased delivery

1. **MVP:** layout, file explorer, Monaco, chat + one Bedrock call, backend
   unit tests, README/env examples.
2. Project generation (multi-file), conversation history persistence.
3. Terminal panel + sandboxed execution.
4. Auth + project access control.
5. Git integration + integration tests.
6. Deployment: Dockerfiles, Compose, ECS task/service defs.
