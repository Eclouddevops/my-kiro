# Implementation Tasks: AI-Powered IDE

Tasks are grouped by phase. Each references the requirements it satisfies.

## Phase 0 — Repository & tooling

- [ ] 0.1 Create repo layout: `backend/`, `frontend/`, `docker/`, root docs.
- [ ] 0.2 Root `README.md` with setup instructions.
- [ ] 0.3 `.env.example` for backend and frontend.
- [ ] 0.4 `docker-compose.yml` for local dev (db, backend, frontend).

## Phase 1 — MVP

### Backend
- [ ] 1.1 FastAPI app factory, config (pydantic-settings), CORS. (R5)
- [ ] 1.2 `BedrockService.converse()` wrapper + sanitized errors. (R5, R-SEC1)
- [ ] 1.3 In-memory/FS project + file model for MVP; path validation. (R2,R6,R-SEC4)
- [ ] 1.4 `POST /chat` endpoint: assemble context, call Bedrock, return reply
      + proposals. (R4, R7)
- [ ] 1.5 Unit tests for BedrockService (mocked boto3) and validation. (R10)

### Frontend
- [ ] 1.6 Vite React+TS app, dark theme tokens. (R1)
- [ ] 1.7 IDELayout: sidebar + editor + chat + terminal, resizable. (R1)
- [ ] 1.8 FileTree + ProjectList in sidebar. (R2)
- [ ] 1.9 Monaco editor wrapper with tabs + dirty state. (R3)
- [ ] 1.10 Chat panel wired to `/chat`; render reply + proposals. (R4)

## Phase 2 — Project generation & history

- [ ] 2.1 Postgres models + Alembic migrations (users, projects, files,
      messages). (R7, R9)
- [ ] 2.2 Multi-file generation: proposals -> validated apply endpoint. (R6,R-SEC4,R-SEC5)
- [ ] 2.3 Persist conversation history; ContextBuilder with token budget. (R7)
- [ ] 2.4 Proposal review UI (accept/reject per file). (R4, R-SEC5)

## Phase 3 — Terminal & sandboxed execution

- [ ] 3.1 ExecutorService: Docker per-run, non-root, limits, no net,
      timeout. (R8, R-SEC2, R-SEC3)
- [ ] 3.2 WebSocket exec endpoint streaming stdout/stderr. (R8)
- [ ] 3.3 TerminalPanel (xterm.js) wired to the WS stream. (R8)

## Phase 4 — Auth & access control

- [ ] 4.1 JWT auth: register/login/me; password hashing. (R9)
- [ ] 4.2 Project ownership + `project_members`; per-request access checks. (R9)
- [ ] 4.3 Frontend auth flow + token storage + API interceptor. (R9)

## Phase 5 — Git & tests

- [ ] 5.1 GitService: init/status/diff/add/commit/branches. (R10)
- [ ] 5.2 Source-control sidebar view. (R2, R10)
- [ ] 5.3 Integration tests (API via httpx + test DB). (R10)
- [ ] 5.4 Frontend component tests (Vitest + RTL). (R10)

## Phase 6 — Deployment

- [ ] 6.1 Backend + frontend Dockerfiles. (NFR portability)
- [ ] 6.2 ECS task + service definitions; env/secret wiring. (NFR)
- [ ] 6.3 Deployment docs in README.

## Definition of done (per feature)

- Implemented, builds cleanly, and has at least one test exercising it.
- No secrets in client code or responses.
- Destructive/exec actions gated behind validation/approval.
- Documented in README (setup, env, how to run/test).
