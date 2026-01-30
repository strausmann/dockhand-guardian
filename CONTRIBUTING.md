# 🤝 Contributing to Dockhand Guardian

Thank you for your interest in contributing to Dockhand Guardian! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## 📜 Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct. By participating, you are expected to uphold this code.

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

## 💻 Development Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Node.js (for commit tooling)

### Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Development tooling (commitizen, commitlint, husky)
npm install
```

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
pytest test_guardian.py

# Run with coverage
pytest --cov=guardian test_guardian.py

# Run linting
make lint

# Run all checks
make check
```

## 📝 Commit Guidelines

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning and changelog generation.

### Commit Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Commit Types

| Type | Description | Release Impact |
|------|-------------|----------------|
| `feat` | New feature | 🔼 Minor version |
| `fix` | Bug fix | 🔼 Patch version |
| `perf` | Performance improvement | 🔼 Patch version |
| `refactor` | Code refactoring | 🔼 Patch version |
| `build` | Build system changes | 🔼 Patch version |
| `docs` | Documentation only | ⏸️ No release |
| `ci` | CI/CD changes | ⏸️ No release |
| `test` | Test changes | ⏸️ No release |
| `style` | Code style changes | ⏸️ No release |
| `chore` | Maintenance tasks | ⏸️ No release |

### Required Scopes

Every commit **must** include a scope. See [.github/SCOPES.md](.github/SCOPES.md) for available scopes:

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

```bash
# Interactive commit helper
npm run commit

# Or use git directly
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
   make check
   pytest
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
   - ✅ Commit message validation
   - ✅ Python linting (flake8, black, isort)
   - ✅ Tests passing
   - ✅ Docker build successful

## 🚢 Release Process

This project uses [semantic-release](https://github.com/semantic-release/semantic-release) for automated versioning and releases.

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
- 🐳 Docker image (if configured)

## 💡 Development Tips

### Using the Makefile

```bash
make help          # Show all available commands
make install       # Install Python dependencies
make test          # Run tests
make lint          # Run linting
make check         # Run all checks
make commit        # Interactive commit (commitizen)
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
