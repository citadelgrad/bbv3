# MLB Fantasy Development Environment
# Manages the API, Jobs, and Web services

API_DIR := $(shell pwd)/mlb_fantasy_api
JOBS_DIR := /Users/scott/projects/mlb_fantasy_jobs
WEB_DIR := $(shell pwd)/mlb_fantasy_web

.PHONY: up down restart logs status ps api-logs jobs-logs db-migrate help web-dev web-build web-install

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start all development services
	@echo "Starting MLB Fantasy API..."
	@cd $(API_DIR) && podman compose up -d
	@echo "Starting MLB Fantasy Jobs..."
	@cd $(JOBS_DIR) && podman compose up -d
	@echo "\n✓ All services started"
	@$(MAKE) status --no-print-directory

down: ## Stop all development services
	@echo "Stopping MLB Fantasy Jobs..."
	@cd $(JOBS_DIR) && podman compose down
	@echo "Stopping MLB Fantasy API..."
	@cd $(API_DIR) && podman compose down
	@echo "\n✓ All services stopped"

restart: down up ## Restart all services

status: ## Show service URLs and health
	@echo "\n=== Service URLs ==="
	@echo "Web:        http://localhost:3000"
	@echo "API:        http://localhost:8000/docs"
	@echo "Jobs API:   http://localhost:8001/docs"
	@echo "Flower:     http://localhost:5555"
	@echo ""
	@echo "=== Health Checks ==="
	@curl -sf http://localhost:3000 > /dev/null 2>&1 && echo "Web:        ✓ running" || echo "Web:        ✗ not running"
	@curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1 && echo "API:        ✓ healthy" || echo "API:        ✗ not running"
	@curl -sf http://localhost:8001/api/v1/health > /dev/null 2>&1 && echo "Jobs API:   ✓ healthy" || echo "Jobs API:   ✗ not running"

ps: ## Show running containers
	@echo "\n=== MLB Fantasy API ===" 
	@cd $(API_DIR) && podman compose ps 2>/dev/null | grep -v "Executing external" || true
	@echo "\n=== MLB Fantasy Jobs ==="
	@cd $(JOBS_DIR) && podman compose ps 2>/dev/null | grep -v "Executing external" || true

logs: ## Tail logs from all services (Ctrl+C to exit)
	@echo "Tailing logs from all services..."
	@(cd $(API_DIR) && podman compose logs -f 2>/dev/null | sed 's/^/[API] /' &); \
	 (cd $(JOBS_DIR) && podman compose logs -f 2>/dev/null | sed 's/^/[JOBS] /')

api-logs: ## Tail API logs only
	@cd $(API_DIR) && podman compose logs -f 2>/dev/null | grep -v "Executing external"

jobs-logs: ## Tail Jobs logs only
	@cd $(JOBS_DIR) && podman compose logs -f 2>/dev/null | grep -v "Executing external"

db-migrate: ## Run database migrations for both projects
	@echo "Running API migrations..."
	@cd $(API_DIR) && uv run alembic upgrade head
	@echo "Running Jobs migrations..."
	@cd $(JOBS_DIR) && uv run alembic upgrade head
	@echo "\n✓ Migrations complete"

test: ## Run tests for both projects
	@echo "Testing API..."
	@cd $(API_DIR) && uv run pytest
	@echo "\nTesting Jobs..."
	@cd $(JOBS_DIR) && uv run pytest

# Web Frontend Targets
web-dev: ## Start web development server
	@echo "Starting MLB Fantasy Web..."
	@cd $(WEB_DIR) && npm run dev

web-build: ## Build web for production
	@echo "Building MLB Fantasy Web..."
	@cd $(WEB_DIR) && npm run build

web-install: ## Install web dependencies
	@echo "Installing web dependencies..."
	@cd $(WEB_DIR) && npm install
