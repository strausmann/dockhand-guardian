# 🤝 Contributing to Dockhand Guardian

Thank you for your interest in contributing to Dockhand Guardian! This document provides guidelines
and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## 📜 Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) Code of
Conduct. By participating, you are expected to uphold this code.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dockhand-guardian.git
   cd dockhand-guardian
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/strausmann/dockhand-guardian.git
   ```

## � Repository Structure

Understanding the project layout:

```
dockhand-guardian/
├── src/                    # 🐍 Application source code
│   ├── __init__.py         # Package initialization
│   └── guardian.py         # Main watchdog logic
│
├── tests/                  # 🧪 Test suite
│   └── test_guardian.py    # Unit tests
│
├── docker/                 # 🐳 Container configuration
│   ├── Dockerfile          # Multi-stage build definition
│   └── docker-compose.yml  # Example deployment stack
│
├── docs/                   # 📚 Documentation
│   ├── README.md           # Main documentation
│   ├── CONTRIBUTING.md     # This file
│   ├── WEBHOOKS.md         # Notification setup guide
│   └── CHANGELOG.md        # Release history (auto-generated)
│
├── .github/                # ⚙️ GitHub automation
│   ├── workflows/          # CI/CD pipelines
│   │   ├── test.yml        # Python tests & Docker build
│   │   ├── lint.yml        # Code quality checks
│   │   ├── release.yml     # Semantic release
│   │   ├── docker-publish.yml  # Image publishing
│   │   └── dependabot-auto-merge.yml  # Auto-merge deps
│   ├── ISSUE_TEMPLATE/     # Issue templates
│   ├── SCOPES.md           # Commit scope reference
│   └── dependabot.yml      # Dependency updates
│
└── Configuration files     # 📝 Project configuration
    ├── pyproject.toml      # Python dependencies & project config
    ├── package.json        # npm dev tools (semantic-release)
    ├── Makefile            # Development commands
    ├── .releaserc.json     # Semantic release config
    ├── .prettierrc.json    # Code formatting
    ├── .commitlintrc.json  # Commit message validation
    └── .husky/             # Git hooks
```

### Key Points

- **Symlinks in root**: README, CHANGELOG, Dockerfile, docker-compose.yml link to their actual
  locations
- **No code in root**: All application code is in `src/`
- **Tests separate**: All tests in dedicated `tests/` directory
- **Docker isolated**: Build files in `docker/` directory
- **Docs centralized**: All documentation in `docs/` directory

## �💻 Development Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Node.js (for commit tooling)

### Install Dependencies

```bash
# Python dependencies
pip install -e .[dev]

# Development tooling (commitizen, commitlint, husky)
npm install

# Install pre-commit hooks
pre-commit install
```

### Code Quality Tools

This project uses modern Python tooling for code quality:

- **[Ruff](https://docs.astral.sh/ruff/)** - Ultra-fast linter and formatter (replaces flake8,
  black, isort, pylint)
- **[mypy](https://mypy-lang.org/)** - Static type checking
- **[pre-commit](https://pre-commit.com/)** - Automated Git hooks
- **[prettier](https://prettier.io/)** - YAML, Markdown, and JSON formatting
- **[pytest](https://pytest.org/)** - Testing framework with coverage

```bash
# Manual code quality checks
make lint              # Run ruff linting
make format            # Auto-format with ruff & prettier
make format-check      # Check formatting without changes
make type-check        # Run mypy type checking
make test              # Run tests with coverage

# Run all checks
pre-commit run --all-files
```

### Automatic Pre-Commit Checks

When you commit (via `git commit` or `make commit`), **all quality checks run automatically** via
pre-commit hooks:

1. 🔍 **make check** - Runs all quality checks in one step:
   - ✨ Ruff linting and formatting
   - 🔍 mypy type checking
   - 📝 prettier formatting (YAML/JSON/Markdown)
   - 🧪 pytest test suite
2. ✂️ **Trailing whitespace** - Removes trailing spaces
3. 📝 **File fixers** - Fixes end of files
4. ✅ **Validators** - Checks YAML/JSON syntax

> [!IMPORTANT] **Every commit now runs `make check` automatically**, including all tests. This
> ensures no commit can bypass quality checks, whether you use `git commit -m "..."` or
> `make commit`.

#### What happens if hooks modify files?

If pre-commit hooks auto-format your files (e.g., prettier, ruff), the commit will **fail** with a
message like:

```
prettier.................................................................Failed
- hook id: prettier
- files were modified by this hook

your-file.json
```

**This is expected behavior!** The hooks have automatically fixed your files. You need to:

1. **Stage the auto-formatted files:**
   ```bash
   git add -A
   ```
2. **Commit again:**
   ```bash
   git commit -m "your message"
   ```

**Example workflow:**

```bash
# First attempt - hooks auto-format files
$ git commit -m "feat(webhook): add new notification service"
prettier.................................................................Failed
- files were modified by this hook

# Stage the formatted files and try again
$ git add -A
$ git commit -m "feat(webhook): add new notification service"
ruff.....................................................................Passed
prettier.................................................................Passed
mypy.....................................................................Passed
pytest...................................................................Passed
[main abc1234] feat(webhook): add new notification service
```

> [!TIP] To avoid surprises, run `make format` before committing. This formats all files upfront so
> the commit succeeds on the first try.

#### Do pre-commit hooks guarantee CI success?

Pre-commit hooks catch **almost all CI failures**:

**✅ Covered by pre-commit hooks:**

- ✅ Ruff linting and formatting
- ✅ mypy type checking
- ✅ prettier formatting (YAML, JSON, Markdown)
- ✅ pytest tests (all test suite)
- ✅ YAML/JSON syntax validation

**⚠️ NOT covered by pre-commit hooks:**

- **Commit message validation** (commitlint) - Only runs in CI on PRs
- **Docker build** - Only runs in CI

**To simulate full CI locally:**

```bash
# Run all local checks
make check

# Validate commit message format
make validate-commit

# Test Docker build
make build

# Or run everything locally
make ci-local

# Check GitHub Actions status
make ci-status

# View logs of latest workflow
make ci-logs

# Watch currently running workflows
make ci-watch
```

**Or run the full CI simulation:**

```bash
make check && npx commitlint --from HEAD~1 && make build
```

This checks everything that CI will check!

### Local Development

```bash
# Set environment variables
export MONITORED_CONTAINERS=dockhand-app,dockhand-database
export GRACE_SECONDS=60
export STACK_DIR=/path/to/your/stack

# Run guardian locally
python guardian.py

# Or use Docker Compose
docker compose up -d
docker compose logs -f guardian
```

### Running Tests

```bash
# Run tests with pytest
make test

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_guardian.py::test_environment_parsing -v
```

### Code Quality Checks

```bash
# Lint Python code
make lint

# Format code (auto-fix)
make format

# Check formatting only
make format-check

# Type checking
make type-check

# Run all pre-commit checks
pre-commit run --all-files

# Run all quality checks (recommended before PR)
make check
```

> [!TIP] **`make check` vs CI Workflows:**
>
> `make check` covers most CI checks:
>
> - ✅ Ruff linting (`lint.yml`)
> - ✅ Ruff formatting (`lint.yml`)
> - ✅ Prettier formatting (`lint.yml`)
> - ✅ mypy type checking (`lint.yml`)
> - ✅ pytest tests (`test.yml`)
> - ✅ Quick ruff check (`test.yml`)
>
> **Not covered by `make check`:**
>
> - ⚠️ **Commit message validation** - Use `npx commitlint --from HEAD~1` to check locally
> - ⚠️ **Docker build** - Use `make build` or `docker build -f docker/Dockerfile .`
>
> For complete CI simulation, run:
>
> ```bash
> make check && npx commitlint --from HEAD~1 && make build
> ```

## 📝 Commit Guidelines

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated
versioning and changelog generation.

### Commit Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Commit Types

| Type       | Description             | Release Impact   | Docker Image     |
| ---------- | ----------------------- | ---------------- | ---------------- |
| `feat`     | New feature             | 🔼 Minor version | ✅ Published     |
| `fix`      | Bug fix                 | 🔼 Patch version | ✅ Published     |
| `perf`     | Performance improvement | 🔼 Patch version | ✅ Published     |
| `refactor` | Code refactoring        | 🔼 Patch version | ✅ Published     |
| `build`    | Build system changes    | 🔼 Patch version | ✅ Published     |
| `docs`     | Documentation only      | ⏸️ No release    | ❌ Not published |
| `ci`       | CI/CD changes           | ⏸️ No release    | ❌ Not published |
| `test`     | Test changes            | ⏸️ No release    | ❌ Not published |
| `style`    | Code style changes      | ⏸️ No release    | ❌ Not published |
| `chore`    | Maintenance tasks       | ⏸️ No release    | ❌ Not published |

### Required Scopes

Every commit **must** include a scope. See [.github/SCOPES.md](.github/SCOPES.md) for available
scopes:

- `guardian` - Core guardian logic
- `docker` - Docker-related changes
- `compose` - Docker Compose configuration
- `webhook` - Notification system
- `monitoring` - Health check logic
- `recovery` - Recovery process
- `ci` - CI/CD workflows
- `deps` - Dependencies
- `docs` - Documentation
- `config` - Configuration
- `release` - Release automation

### Using Commitizen (Recommended)

Commitizen provides an interactive wizard to create properly formatted commits with **automatic
scope selection** based on the commit type:

```bash
# Interactive commit helper (includes quality checks)
npm run commit
```

This command will:

1. **Run `make check`** - Validates code quality, tests, formatting
2. **Launch commitizen wizard** - If checks pass
3. **Guide you through commit creation:**
   - **Type selection** (feat, fix, docs, etc.) - Choose from dropdown
   - **Scope selection** (guardian, docker, webhook, etc.) - Filtered dropdown based on type
   - Short description
   - Long description (optional)
   - Breaking changes (optional)
   - Related issues (optional)

> [!TIP] Commitizen filters available scopes based on the selected type. For example:
>
> - `feat` → shows guardian, webhook, monitoring, recovery scopes
> - `ci` → only shows ci scope
>
> See [.github/SCOPES.md](../.github/SCOPES.md) for detailed type+scope combinations and examples.

> [!NOTE] `npm run commit` automatically runs `make check` before the wizard. If quality checks
> fail, fix the issues and run the command again.

**Or use git directly** if you're familiar with the format:

```bash
# Run checks manually first
make check

# Then commit
git commit -m "feat(monitoring): add TCP port health check"
```

### Examples

```bash
# Feature that triggers a release
git commit -m "feat(webhook): add Telegram notification support"

# Bug fix that triggers a release
git commit -m "fix(recovery): handle timeout during docker compose pull"

# Documentation change (no release)
git commit -m "docs(readme): update webhook configuration examples"

# CI change (no release)
git commit -m "ci(workflow): add code coverage reporting"

# Breaking change (major release)
git commit -m "feat(config)!: change MONITORED_CONTAINERS environment variable format

BREAKING CHANGE: MONITORED_CONTAINERS now uses semicolon separator instead of comma"
```

## 🔄 Pull Request Process

1. **Create a feature branch** from `main`:

   ```bash
   git checkout -b feat/my-new-feature
   ```

2. **Make your changes** following the commit guidelines

3. **Update documentation** if needed (README.md, WEBHOOKS.md, etc.)

4. **Test your changes**:

   ```bash
   # Run all tests
   make test

   # Run linting
   make lint

   # Check formatting
   make format-check

   # Type checking
   make type-check

   # Or run all pre-commit checks
   pre-commit run --all-files
   ```

5. **Push to your fork**:

   ```bash
   git push origin feat/my-new-feature
   ```

6. **Open a Pull Request** on GitHub with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots/logs if applicable

7. **Wait for review** - maintainers will review your PR and may request changes

8. **CI checks must pass**:
   - ✅ Commit message validation (commitlint)
   - ✅ Python linting (ruff)
   - ✅ Type checking (mypy)
   - ✅ Code formatting (ruff, prettier)
   - ✅ Tests passing (pytest)
   - ✅ Docker build successful

## 🚢 Release Process

This project uses [semantic-release](https://github.com/semantic-release/semantic-release) for
automated versioning and releases.

### Automated Releases

- Releases are **automatically triggered** when changes are merged to `main`
- Version numbers are determined by commit types:
  - `feat` → Minor version bump (1.0.0 → 1.1.0)
  - `fix`, `perf`, `refactor`, `build` → Patch version bump (1.0.0 → 1.0.1)
  - `feat!` or `BREAKING CHANGE:` → Major version bump (1.0.0 → 2.0.0)

### What Gets Released

Only commits with these types trigger releases:

- ✅ `feat` - New features
- ✅ `fix` - Bug fixes
- ✅ `perf` - Performance improvements
- ✅ `refactor` - Code refactoring
- ✅ `build` - Build system changes

These types do **NOT** trigger releases:

- ⏸️ `docs` - Documentation changes
- ⏸️ `ci` - CI/CD workflow changes
- ⏸️ `test` - Test changes
- ⏸️ `style` - Code style/formatting
- ⏸️ `chore` - Maintenance tasks

### Release Contents

Each release includes:

- 📋 Updated CHANGELOG.md with emoji sections
- 🏷️ Git tag (e.g., `v1.2.0`)
- 📦 GitHub Release with release notes
- 🐳 Docker images automatically published to GitHub Container Registry
  - `ghcr.io/strausmann/dockhand-guardian:latest`
  - `ghcr.io/strausmann/dockhand-guardian:1.2.0`
  - `ghcr.io/strausmann/dockhand-guardian:1.2`
  - `ghcr.io/strausmann/dockhand-guardian:1`
  - Multi-platform support: `linux/amd64`, `linux/arm64`

### Dependency Updates

Dependabot runs **daily** at 03:00 UTC and checks:

| Ecosystem             | Commit Type   | Release Impact                    | Auto-Merge          |
| --------------------- | ------------- | --------------------------------- | ------------------- |
| 🐳 Docker base images | `fix(deps)`   | ✅ Patch release + Docker publish | ✅ Patch/Minor only |
| 🐍 Python packages    | `fix(deps)`   | ✅ Patch release + Docker publish | ✅ Patch/Minor only |
| ⚙️ GitHub Actions     | `chore(deps)` | ❌ No release                     | ✅ Patch/Minor only |
| 📦 npm packages       | `chore(deps)` | ❌ No release                     | ✅ Patch/Minor only |

**Automatic Merge Behavior:**

- ✅ **Patch updates** (1.2.3 → 1.2.4): Auto-approved and auto-merged after CI passes
- ✅ **Minor updates** (1.2.0 → 1.3.0): Auto-approved and auto-merged after CI passes
- ⚠️ **Major updates** (1.0.0 → 2.0.0): Requires manual review (potential breaking changes)

**Important:** Production-relevant dependency updates (Docker, Python) automatically trigger:

1. Patch version bump (e.g., `1.2.3` → `1.2.4`)
2. New GitHub Release
3. Docker image build and publish to GHCR
4. Multi-platform builds (amd64 + arm64)
5. Fully automated from Dependabot PR → Release → Docker Image

## 💡 Development Tips

### Using the Makefile

```bash
make help          # Show all available commands
make install       # Install Python dependencies
make test          # Run tests
make lint          # Run linting
make check         # Run all checks
make commit        # Interactive commit (commitizen)
make amend         # Add changes to last commit
make push          # Pull with rebase and push
make clean         # Clean build artifacts
```

### Testing Webhook Notifications

```bash
# Set webhook URL for testing
export WEBHOOK_URLS="discord://your_webhook_id/token"

# Stop a container to trigger recovery
docker stop dockhand-app

# Watch guardian logs
docker compose logs -f guardian
```

### Maintenance Mode Testing

```bash
# Enable maintenance mode
touch .maintenance

# Verify guardian skips checks
docker compose logs -f guardian

# Disable maintenance mode
rm .maintenance
```

## 🐛 Reporting Bugs

Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) template when filing issues.

Include:

- Guardian version
- Docker version
- Python version
- Configuration (environment variables)
- Logs showing the error
- Steps to reproduce

## 💡 Suggesting Features

Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) template.

Describe:

- Use case and problem to solve
- Proposed solution
- Alternative solutions considered
- Additional context

## 📚 Additional Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## 🙏 Recognition

Contributors will be recognized in:

- GitHub contributors list
- Release notes (for significant contributions)
- Future CONTRIBUTORS.md file

## 📧 Questions?

If you have questions about contributing, feel free to:

- Open a [Discussion](https://github.com/strausmann/dockhand-guardian/discussions)
- Comment on an existing issue
- Reach out to the maintainer

---

Thank you for contributing to Dockhand Guardian! 🛡️
