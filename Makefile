.PHONY: help install update build test lint format format-check type-check check coverage commit push rebase-continue rebase-abort diff log sync clean docker-up docker-down docker-logs docker-restart docker-clean release-dry-run release-notes release status version

help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  Dockhand Guardian - Entwicklungsumgebung                  ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📚 REPOSITORY STRUKTUR:"
	@echo "  src/                 → Main application code"
	@echo "  tests/               → Unit tests"
	@echo "  docker/              → Docker & docker-compose files"
	@echo "  docs/                → Documentation (README, CONTRIBUTING)"
	@echo ""
	@echo "🚀 VERFÜGBARE BEFEHLE:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install         Install all dependencies (Python + npm)"
	@echo "  make update          Update all dependencies"
	@echo ""
	@echo "Entwicklung:"
	@echo "  make build           Build Docker image"
	@echo "  make test            Run tests"
	@echo "  make coverage        Run tests and open coverage report"
	@echo "  make lint            Code quality checks"
	@echo "  make format          Format code with ruff & prettier"
	@echo "  make format-check    Check code formatting"
	@echo "  make type-check      Run mypy type checking"
	@echo "  make check           Run all quality checks (lint + format-check + type-check + test)"
	@echo ""
	@echo "Git Workflow:"
	@echo "  make commit          Interactive commit with quality checks (commitizen)"
	@echo "  make amend           Add changes to last commit (git commit --amend)"
	@echo "  make push            Pull with rebase and push to remote"
	@echo "  make diff            Show unstaged changes"
	@echo "  make log             Show formatted git log"
	@echo "  make sync            Fetch and show repository status"
	@echo "  make rebase-continue Continue rebase after resolving conflicts"
	@echo "  make rebase-abort    Abort rebase and return to previous state"
	@echo ""
	@echo "Docker Management:"
	@echo "  make docker-up       Start containers"
	@echo "  make docker-down     Stop containers"
	@echo "  make docker-logs     Show container logs"
	@echo "  make docker-restart  Restart guardian container"
	@echo "  make docker-clean    Remove old Docker images and volumes"
	@echo ""
	@echo "Release Management:"
	@echo "  make release-dry-run Test semantic release (without pushing)"
	@echo "  make release-notes   Show generated release notes"
	@echo "  make release         Execute manual release (with confirmation)"
	@echo ""
	@echo "Wartung:"
	@echo "  make status          Show service status"
	@echo "  make clean           Cleanup containers and images"
	@echo "  make version         Show current version"

install:
	@echo "📦 Installing dependencies..."
	@echo ""
	@echo "1️⃣  Python dependencies..."
	@pip3 install -e .[dev]
	@echo ""
	@echo "2️⃣  npm dependencies..."
	@npm install
	@echo ""
	@echo "3️⃣  Installing pre-commit hooks..."
	@pre-commit install
	@echo ""
	@echo "✅ All dependencies installed!"

update:
	@echo "🔄 Updating dependencies..."
	@echo ""
	@echo "1️⃣  Updating Python dependencies..."
	@pip3 install --upgrade -e .[dev]
	@echo ""
	@echo "2️⃣  Updating npm dependencies..."
	@npm update
	@echo ""
	@echo "3️⃣  Updating pre-commit hooks..."
	@pre-commit autoupdate
	@echo ""
	@echo "✅ All dependencies updated!"

build:
	@echo "🔨 Building Docker image..."
	docker build -f docker/Dockerfile -t dockhand-guardian:latest .

test:
	@echo "🧪 Running tests..."
	python3 -m pytest tests/ -v

coverage:
	@echo "🧪 Running tests with coverage..."
	@python3 -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo ""
	@echo "📊 Opening coverage report..."
	@python3 -m webbrowser -t "file://$(PWD)/htmlcov/index.html" 2>/dev/null || \
		(command -v xdg-open >/dev/null && xdg-open htmlcov/index.html) || \
		(command -v open >/dev/null && open htmlcov/index.html) || \
		echo "⚠️  Coverage report generated in htmlcov/index.html"

lint:
	@echo "🔍 Checking code quality..."
	@ruff check src/ tests/
	@echo "✅ Linting complete"

format:
	@echo "✨ Formatting code..."
	@ruff format src/ tests/
	@ruff check --fix src/ tests/
	@npm run format
	@echo "✅ Formatting complete"

format-check:
	@echo "🔍 Checking code formatting..."
	@ruff format --check src/ tests/
	@npm run format:check

type-check:
	@echo "🔍 Type checking..."
	@mypy src/ --ignore-missing-imports

check:
	@echo "🔍 Running all quality checks..."
	@echo ""
	@echo "1️⃣  Linting..."
	@ruff check src/ tests/
	@echo ""
	@echo "2️⃣  Format checking..."
	@ruff format --check src/ tests/
	@npm run format:check
	@echo ""
	@echo "3️⃣  Type checking..."
	@mypy src/ --ignore-missing-imports
	@echo ""
	@echo "4️⃣  Running tests..."
	@python3 -m pytest tests/ -v
	@echo ""
	@echo "✅ All checks passed!"

commit:
	@echo "📝 Starting interactive commit with quality checks..."
	@npm run commit

amend:
	@echo "📝 Adding changes to last commit..."
	@git add -A
	@git commit --amend --no-edit
	@echo ""
	@echo "✅ Changes added to last commit!"
	@echo "⚠️  Run 'git push --force-with-lease' to update remote (only if already pushed)"

push:
	@echo "🔄 Pulling latest changes with rebase..."
	@git pull --rebase
	@echo ""
	@echo "⬆️  Pushing to remote..."
	@git push
	@echo ""
	@echo "✅ Successfully pushed!"

rebase-continue:
	@echo "▶️  Continuing rebase..."
	@git rebase --continue
	@echo ""
	@echo "✅ Rebase continued! Run 'make push' to push changes."

rebase-abort:
	@echo "❌ Aborting rebase..."
	@git rebase --abort
	@echo ""
	@echo "✅ Rebase aborted. Repository returned to previous state."

diff:
	@echo "📝 Showing unstaged changes..."
	@git diff

log:
	@echo "📜 Git commit history..."
	@git log --oneline --graph --decorate --all -20

sync:
	@echo "🔄 Fetching remote changes..."
	@git fetch --all --tags
	@echo ""
	@echo "📊 Repository status:"
	@git status -sb
	@echo ""
	@echo "📌 Local branches:"
	@git branch -vv

docker-up:
	@echo "🚀 Starting containers..."
	docker-compose -f docker/docker-compose.yml up -d
	@sleep 2
	@echo "✅ Containers started"

docker-down:
	@echo "🛑 Stopping containers..."
	docker-compose -f docker/docker-compose.yml down

docker-logs:
	@echo "📋 Showing logs..."
	docker-compose -f docker/docker-compose.yml logs -f guardian

docker-restart:
	@echo "🔄 Restarting guardian..."
	docker-compose -f docker/docker-compose.yml restart guardian
	@sleep 2
	@echo "✅ Guardian restarted"

docker-clean:
	@echo "🧹 Cleaning up Docker resources..."
	@echo ""
	@echo "Removing stopped containers..."
	@docker container prune -f
	@echo ""
	@echo "Removing unused images..."
	@docker image prune -a -f
	@echo ""
	@echo "Removing unused volumes..."
	@docker volume prune -f
	@echo ""
	@echo "✅ Docker cleanup complete!"

status:
	@echo "📊 Container status:"
	@docker-compose -f docker/docker-compose.yml ps

version:
	@echo "Version: $$(git describe --tags --abbrev=0 2>/dev/null || echo 'unreleased')"
	@git status --short | head -5

release-dry-run:
	@echo "🚀 Testing Semantic Release (Dry-Run)..."
	@echo ""
	@npx semantic-release --dry-run 2>&1 | grep -E "✔|✘|The (next|release|Repository)" || true

release-notes:
	@echo "📝 Generated Release Notes:"
	@echo ""
	@npx semantic-release --dry-run 2>&1 | grep -A 50 "Release note for version" | head -60

release:
	@echo "🚀 Executing Semantic Release..."
	@echo ""
	@echo "⚠️  This will:"
	@echo "   • Sync Git tags"
	@echo "   • Analyze commits"
	@echo "   • Calculate version"
	@echo "   • Update CHANGELOG.md"
	@echo "   • Create Git tag"
	@echo "   • Publish GitHub release"
	@echo "   • Push changes to Git"
	@echo ""
	@read -p "Continue? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "📥 Syncing Git tags..."; \
		git fetch --all --tags --force; \
		echo "✅ Git tags synced"; \
		echo ""; \
		CI=true npx semantic-release; \
	else \
		echo "Release aborted."; \
	fi

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker rmi dockhand-guardian:latest 2>/dev/null || true
	@echo "✅ Cleanup complete"
