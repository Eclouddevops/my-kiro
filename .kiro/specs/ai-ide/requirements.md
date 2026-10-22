# Requirements: AI-Powered IDE

## Overview

A web-based AI development environment inspired by modern AI coding IDEs. Users
manage projects, edit source code in a Monaco-based editor, and collaborate with
an LLM (Amazon Bedrock) to describe applications and request code changes. The
system supports authentication, project-level access control, Git integration,
isolated code execution, and automated tests.

## Actors

- **Developer (end user):** creates projects, edits files, chats with the AI,
  runs builds/tests, and commits via Git.
- **System / Backend:** mediates all LLM access, persists metadata, enforces
  access control, and runs generated code in isolation.

## Functional requirements

### R1 — IDE interface

- The UI SHALL present a professional, dark-themed IDE layout.
- The layout SHALL contain: activity/side bar, file explorer, editor area,
  AI chat panel, and a bottom terminal panel.
- The layout SHALL be resizable (panels can be collapsed/expanded).

### R2 — Project & file navigation

- Users SHALL see a left sidebar listing projects, files, and folders.
- The sidebar SHALL include a source-control view showing Git status.
- Users SHALL be able to open, create, rename, and delete files and folders
  (destructive actions require confirmation — see R-SEC5).

### R3 — Code editor

- The editor SHALL use Monaco Editor.
- The editor SHALL support syntax highlighting, multiple open tabs, and
  save-on-command.
- The editor SHALL reflect unsaved-change state per tab.

### R4 — AI chat panel

- Users SHALL be able to describe applications and request code changes in
  natural language.
- The panel SHALL stream or display LLM responses and any proposed file
  operations.
- Proposed file operations SHALL be reviewable before they are applied
  (see R-SEC5).

### R5 — Secure LLM integration

- The backend SHALL integrate Amazon Bedrock via the AWS SDK.
- LLM credentials and AWS keys SHALL NEVER be exposed to the frontend.
- All model calls SHALL be proxied through authenticated backend endpoints.

### R6 — Project generation

- Users SHALL be able to create a project and have the AI generate multiple
  source files in one request.
- Generated file operations SHALL be validated (path traversal prevention,
  size limits, allowed extensions) before being written.

### R7 — Conversation history & context

- The system SHALL persist conversation history per project.
- The backend SHALL assemble relevant project context (open files, file tree,
  recent messages) when calling the LLM, within a token budget.

### R8 — Terminal panel

- A terminal panel SHALL display build output and test results.
- Output SHALL stream from backend execution of commands run in isolation.

### R9 — Authentication & access control

- The system SHALL support user authentication (JWT-based).
- Each project SHALL have an owner; access SHALL be enforced at the API layer.
- Users SHALL only access projects they own or are shared with.

### R10 — Git integration & automated tests

- The system SHALL support Git operations: init, status, diff, stage, commit,
  and branch listing for a project.
- The codebase SHALL include unit tests and integration tests with a documented
  way to run them.

## Security requirements

- **R-SEC1:** No LLM/AWS credentials in the frontend or in client-visible
  responses.
- **R-SEC2:** Generated code SHALL run only in isolated, restricted execution
  environments (containerized, non-root, read-only base where possible).
- **R-SEC3:** Execution SHALL apply resource limits (CPU, memory, PIDs),
  network restrictions, and timeouts.
- **R-SEC4:** All AI-generated file operations SHALL be validated against an
  allow-list and the project root (no path traversal, no absolute paths).
- **R-SEC5:** Potentially destructive actions (delete, overwrite outside diff,
  shell execution) SHALL require explicit user approval.

## Non-functional requirements

- **Performance:** editor interactions remain responsive; LLM calls are async
  and non-blocking in the UI.
- **Portability:** runs locally via Docker Compose; deployable to AWS ECS.
- **Observability:** structured logging on the backend; errors surfaced to the
  UI without leaking secrets.
- **Testability:** backend and frontend each have a runnable test suite.

## Acceptance criteria (MVP)

1. User can open the app and see a dark IDE with sidebar, editor, chat, terminal.
2. User can create a project and open/edit a file in Monaco.
3. User can send a chat message and receive an LLM response from the backend
   (Bedrock), with no credentials in the browser.
4. Backend has passing unit tests; `README` documents setup and env vars.
