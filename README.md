# AI-Powered IDE

A web-based AI development environment: a dark-themed IDE with a file explorer,
Monaco code editor, an AI chat panel backed by Amazon Bedrock, a terminal for
build/test output, Git integration, authentication, and sandboxed code
execution.

> Status: MVP under active construction. See
> [`.kiro/specs/ai-ide/`](.kiro/specs/ai-ide/) for requirements, design, and the
> phased task plan. A feature is only documented as "working" here once it is
> implemented and tested.

## Architecture

| Layer      | Technology                                            |
|------------|-------------------------------------------------------|
| Frontend   | React + TypeScript + Vite, Monaco Editor, xterm.js    |
| Backend    | Python FastAPI (async), SQLAlchemy 2 + Alembic        |
| AI         | Amazon Bedrock via AWS SDK (boto3 `bedrock-runtime`)  |
| Storage    | PostgreSQL (metadata), S3 (artifacts)                 |
| Auth       | JWT (python-jose) + bcrypt (passlib)                  |
| Execution  | Docker-isolated per-run sandbox (no net, limits)      |
| Deploy     | Docker Compose (local), AWS ECS (target)              |

See [`.kiro/specs/ai-ide/design.md`](.kiro/specs/ai-ide/design.md) for the full
architecture and API surface.

## Repository layout

```
backend/     FastAPI service (API, services, security, tests)
frontend/    React + TypeScript SPA (IDE UI)
docker/      Dockerfiles and compose for local dev
.kiro/specs/ requirements, design, and tasks
```

## Prerequisites

- Node.js 20+
- Python 3.11+
- Docker (for Postgres locally and for sandboxed code execution)
- AWS account with Amazon Bedrock model access (for live LLM calls)

## Quick start (local dev)

### 1. Configure environment

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# edit backend/.env with your AWS region, Bedrock model id, and DB URL
```

### 2. Start infrastructure + services

```bash
docker compose -f docker/docker-compose.yml up --build
```

This starts PostgreSQL, the FastAPI backend (http://localhost:8000), and the
Vite dev server (http://localhost:5173).

### 3. Run backend without Docker (optional)

```bash
cd backend
python -m venv .venv && . .venv/Scripts/activate   # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### 4. Run frontend without Docker (optional)

```bash
cd frontend
npm install
npm run dev
```

## Environment variables

See [`backend/.env.example`](backend/.env.example) and
[`frontend/.env.example`](frontend/.env.example). Credentials live only on the
backend and are never exposed to the browser.

## Testing

```bash
# backend
cd backend && pytest

# frontend
cd frontend && npm test
```

## Security notes

- LLM / AWS credentials never reach the frontend; all model calls are proxied
  through authenticated backend endpoints.
- AI-generated file operations are validated (no path traversal, allow-listed
  extensions, size limits) and require user approval before being applied.
- Generated code runs only inside isolated Docker containers with CPU/memory/PID
  limits, no network, and an execution timeout.

## License

MIT (see `LICENSE`).
