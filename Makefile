.PHONY: help build test lint format format-check clean docker-up docker-down docker-logs docker-restart release-dry-run release-notes release status version

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
	@echo "Entwicklung:"
	@echo "  make build           Build Docker image"
	@echo "  make test            Run tests"
	@echo "  make lint            Code quality checks"
	@echo "  make format          Format code with prettier"
	@echo "  make format-check    Check code formatting"
	@echo ""
	@echo "Docker Management:"
	@echo "  make docker-up       Start containers"
	@echo "  make docker-down     Stop containers"
	@echo "  make docker-logs     Show container logs"
	@echo "  make docker-restart  Restart guardian container"
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

build:
	@echo "🔨 Building Docker image..."
	docker build -f docker/Dockerfile -t dockhand-guardian:latest .

test:
	@echo "🧪 Running tests..."
	python3 -m pytest tests/ -v

lint:
	@echo "🔍 Checking code quality..."
	@python3 -m py_compile src/guardian.py && echo "✅ Python syntax OK"
	@python3 -m py_compile tests/test_guardian.py && echo "✅ Test syntax OK"

format:
	@echo "✨ Formatting code..."
	npm run format

format-check:
	@echo "🔍 Checking code formatting..."
	npm run format:check

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
