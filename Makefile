# AI-Powered IDE — developer tasks (macOS / Linux).
#
# On Windows, use the PowerShell steps in the README instead, or run `make`
# from WSL / Git Bash.
#
# Common targets:
#   make setup      install backend + frontend dependencies
#   make dev        run backend + frontend dev servers
#   make test       run all tests
#   make backend    run backend only (uvicorn --reload)
#   make frontend   run frontend only (vite)
#   make build      build the frontend production bundle
#   make up         start the full stack via docker compose
#   make down       stop the docker compose stack
#   make clean      remove virtualenv, node_modules, and build output

SHELL := /bin/bash
ROOT  := $(shell pwd)
PY    := $(ROOT)/backend/.venv/bin/python
PIP   := $(ROOT)/backend/.venv/bin/pip

.DEFAULT_GOAL := help
.PHONY: help setup dev backend frontend test build up down clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup: ## Install backend + frontend dependencies
	./scripts/setup.sh

dev: ## Run backend + frontend dev servers together
	./scripts/dev.sh

backend: ## Run the backend dev server only
	cd backend && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Run the frontend dev server only
	cd frontend && npm run dev

test: ## Run all test suites
	./scripts/test.sh all

build: ## Build the frontend production bundle
	cd frontend && npm run build

up: ## Start the full stack with docker compose
	docker compose -f docker/docker-compose.yml up --build

down: ## Stop the docker compose stack
	docker compose -f docker/docker-compose.yml down

clean: ## Remove venv, node_modules, and build artifacts
	rm -rf backend/.venv backend/.venv-pkgs backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
