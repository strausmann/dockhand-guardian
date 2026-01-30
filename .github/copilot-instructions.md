# Copilot Instructions for Dockhand Guardian

This document provides guidance for GitHub Copilot when working with the Dockhand Guardian project.

## Project Overview

Dockhand Guardian is a Docker sidecar watchdog service that monitors container health and performs
automatic recovery. It's designed to be simple, reliable, and require minimal configuration.

## Architecture

### Core Components

1. **guardian.py**: Main Python application
   - Implements the `ContainerGuardian` class
   - Handles container monitoring via Docker API
   - Manages recovery orchestration
   - Tracks state (failure times, cooldown)

2. **Dockerfile**: Container image definition
   - Based on Python 3.11-slim
   - Includes Docker CLI and docker-compose plugin
   - Installs Python dependencies
   - OCI-compliant image labels for GitHub Container Registry

3. **docker-compose.yml**: Example deployment configuration
   - Shows how to deploy guardian as a sidecar
   - Demonstrates proper volume mounts and networking
   - Includes example monitored services

## Key Design Principles

### 1. Simplicity

- Single Python file for core logic
- Minimal dependencies (docker SDK, requests, apprise)
- Configuration via environment variables only

### 2. Safety

- Grace period prevents premature recovery
- Cooldown prevents recovery loops
- Maintenance mode for controlled operations
- Read-only mounts where possible
- Webhook notifications for visibility via Apprise

### 3. Reliability

- Direct Docker socket communication
- Comprehensive error handling
- Detailed logging at all stages
- State tracking to prevent duplicate actions
- Notification system supporting 80+ services via Apprise

## Configuration System

All configuration uses environment variables:

```python
self.monitored_containers = os.getenv('MONITORED_CONTAINERS', 'dockhand-app,dockhand-database').split(',')
self.grace_seconds = int(os.getenv('GRACE_SECONDS', '300'))
self.check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
self.grace_seconds = int(os.getenv('GRACE_SECONDS', '300'))
self.check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
self.cooldown_seconds = int(os.getenv('COOLDOWN_SECONDS', '600'))
self.webhook_urls = os.getenv('WEBHOOK_URLS', '')
```

### Configuration Guidelines

- Always provide sensible defaults
- Use type conversion for numeric values
- Split comma-separated lists for multiple values
- Document all environment variables

### Webhook System

The guardian uses [Apprise](https://github.com/caronc/apprise) for webhook notifications, supporting
80+ services when recovery actions are triggered:

1. **Discord**: Rich embeds via Apprise Discord integration
2. **Microsoft Teams**: MessageCard format via Apprise
3. **Slack**: Native Slack formatting via Apprise
4. **Email**: SMTP notifications
5. **80+ more services**: Telegram, Pushover, Matrix, etc.

Webhooks are configured via URL-based format (Apprise standard):

```python
WEBHOOK_URLS=discord://webhook_id/token,mailto://user:pass@host.com
```

Webhooks are sent after recovery attempts (both successful and failed) to provide visibility into
guardian actions.

## Monitoring Logic

### Health Check Flow

````
1. Check maintenance mode → Skip if active
2. Check cooldown → Skip if in cooldown
3. For each monitored container:
   a. Check Docker container state
   b. Check Docker health status
   c. Check optional HTTP endpoint
4. Track failure times
5. Check if grace period expired
6. Trigger recovery if needed6. Send webhook notification if recovery triggered```

### State Management

The guardian maintains state in memory:
- `failure_times`: Dictionary tracking when each container first failed
- `last_recovery_time`: Timestamp of last recovery action

## Recovery Process

Recovery is a two-step process:

```bash
# Step 1: Pull latest images
docker compose pull

# Step 2: Recreate containers
docker compose up -d --force-recreate
````

### Recovery Guidelines

- Always execute both steps
- Log each step clearly
- Reset failure tracking after recovery
- Set cooldown even if recovery fails
- Handle subprocess timeouts
- Send webhook notification about recovery result

## Testing Considerations

### Manual Testing Scenarios

1. **Normal Operation**: All containers healthy
2. **Single Container Failure**: One container unhealthy
3. **Multiple Container Failure**: Multiple containers unhealthy
4. **Grace Period**: Verify recovery doesn't trigger early
5. **Maintenance Mode**: Verify monitoring pauses
6. **Cooldown**: Verify recovery doesn't repeat too soon
7. **HTTP Checks**: Verify optional HTTP checks work

### Test Commands

```bash
# Stop a container to trigger failure
docker stop dockhand-app

# Enable maintenance mode
touch .maintenance

# Watch guardian logs
docker compose logs -f guardian

# Verify recovery
docker compose ps
```

## Code Style

### Python Conventions

- Type hints for function signatures
- Docstrings for all classes and methods
- PEP 8 style compliance
- Descriptive variable names
- Comprehensive error handling

### Logging Strategy

- INFO: Normal operations and state changes
- WARNING: Failures, recovery triggers, important state
- ERROR: Exceptions and critical failures
- DEBUG: Detailed diagnostic information

## Common Modifications

### Adding New Health Check Types

To add a new health check type:

1. Add new method to `ContainerGuardian` class
2. Call from `check_container()` method
3. Add configuration via environment variable
4. Update documentation

Example:

```python
def check_tcp_port(self, container_name: str) -> bool:
    """Check if TCP port is reachable."""
    # Implementation here
    pass
```

### Extending Monitored Containers

Containers are dynamically configured via `MONITORED_CONTAINERS`:

- No code changes needed to monitor different containers
- Update environment variable in docker-compose.yml
- Restart guardian service

### Custom Recovery Actions

To customize recovery process:

1. Modify `recover_stack()` method
2. Keep two-step structure (pull + recreate)
3. Maintain logging and error handling
4. Reset state appropriately

## Volume Mounts

Critical volume mounts for guardian:

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro # Docker API access
  - .:/stack:ro # Stack directory for compose commands
```

### Mount Guidelines

- Use read-only (`:ro`) where possible
- Docker socket typically read-only sufficient
- Stack directory needs read access to compose file

## Security Considerations

### Permissions Required

- Read access to Docker socket
- Execute docker CLI commands
- Read access to stack directory

### Security Best Practices

- Run as non-root user when possible
- Use read-only mounts
- Limit network exposure
- Rotate logs to prevent disk fill
- Use Docker secrets for sensitive data

## Troubleshooting Guide

### Common Issues

1. **Container Not Found**
   - Check exact container name
   - Verify container is running
   - Check Docker network connectivity

2. **Permission Denied**
   - Verify socket mount
   - Check socket permissions
   - Verify guardian can execute docker CLI

3. **Recovery Fails**
   - Check compose file syntax
   - Verify stack directory mount
   - Check image availability
   - Review subprocess errors

### Debugging Steps

1. Check guardian logs: `docker compose logs guardian`
2. Verify mounts: `docker inspect dockhand-guardian`
3. Test docker access: `docker compose exec guardian docker ps`
4. Test compose: `docker compose exec guardian docker compose --version`

## Future Enhancements

Potential areas for improvement:

1. **Metrics Export**: Prometheus metrics endpoint
2. **Dashboard**: Simple web UI for status
3. **Multiple Stacks**: Support monitoring multiple compose stacks
4. **Custom Scripts**: Run custom scripts pre/post recovery
5. **Health Check Plugins**: Plugin system for custom health checks

## Contributing Guidelines

When contributing:

1. Maintain backward compatibility
2. Add tests for new features
3. Update documentation
4. Follow existing code style
5. Add logging for new operations
6. Handle errors gracefully

## Development Workflow

### Modern Python Tooling (2025+)

This project uses modern Python standards and tooling:

- **pyproject.toml**: PEP 621 compliant project configuration (replaces setup.py/requirements.txt)
- **Ruff v0.14.14**: Ultra-fast linter and formatter (10-100x faster than flake8/black/isort)
- **mypy v1.19.1**: Static type checking with modern type hints (dict, list, X|None)
- **pre-commit**: Automated Git hooks that run on every commit
- **pytest + pytest-cov**: Testing with coverage reporting
- **prettier**: YAML/JSON/Markdown formatting

### Commit Workflow

All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/) with required
scopes:

```bash
<type>(<scope>): <subject>
```

**Available commit types:**

- `feat`, `fix`, `perf`, `refactor`, `build` → Create releases + Docker images
- `docs`, `ci`, `test`, `style`, `chore` → No release (dev/docs only)

**Required scopes** (see `.commitlintrc.json`):

- `guardian`, `docker`, `compose`, `webhook`, `monitoring`, `recovery`
- `ci`, `deps`, `docs`, `config`, `release`

**Commitizen with scope selection:** The project uses `cz-customizable` (not
`cz-conventional-changelog`) for interactive commits with dropdown scope selection:

```bash
# Use commitizen with automatic quality checks
make commit

# Configuration files:
# - .czrc → Points to cz-customizable adapter
# - .cz-config.js → Defines types, scopes, scopeOverrides
# - package.json → No commitizen config (moved to .czrc)
```

**Scope filtering by type:**

- `feat` → Only shows: guardian, webhook, monitoring, recovery
- `fix` → Shows all scopes
- `ci` → Only shows: ci

See [.github/SCOPES.md](.github/SCOPES.md) for detailed type+scope combinations with 140+ examples.

### Pre-Commit Hooks

**Every commit automatically runs `make check`** via pre-commit hooks (`.pre-commit-config.yaml`):

1. **make check hook** (runs first):
   - Ruff linting (`ruff check`)
   - Ruff + prettier formatting checks
   - mypy type checking
   - Full pytest test suite
2. Additional validators (trailing whitespace, YAML/JSON syntax, etc.)

**This means:**

- ✅ `git commit -m "..."` → Runs full test suite automatically
- ✅ `make commit` → Runs tests twice (once in pre-commit, once in npm script)
- ❌ No commit possible without passing all tests

**Configuration:**

```yaml
# .pre-commit-config.yaml (simplified structure)
repos:
  - repo: local
    hooks:
      - id: make-check
        entry: make check # Runs all quality checks
        always_run: true
```

### Makefile Commands

Comprehensive development commands via Makefile:

**Quality Checks:**

```bash
make check           # All checks (lint + format + type + test)
make lint            # Ruff linting only
make format          # Auto-fix formatting
make format-check    # Check formatting without fixing
make type-check      # mypy type checking
make test            # pytest with coverage
make coverage        # Test coverage + open HTML report
```

**Git Workflow:**

```bash
make commit          # Interactive commit with commitizen + quality checks
make amend           # Add changes to last commit (git add -A && git commit --amend --no-edit)
make push            # Pull with rebase + push (safe)
make diff            # Show unstaged changes
make log             # Pretty git log
make sync            # Fetch + show status
```

**CI/Workflow Validation:**

```bash
make validate-commit    # Validate commit message (commitlint)
make validate-workflows # Check workflow YAML syntax
make ci-local           # Run all CI checks locally
make ci-status          # Show GitHub Actions status (last 10 runs)
make ci-logs            # Show logs from latest workflow
make ci-watch           # Watch currently running workflows
```

**Docker:**

```bash
make build           # Build Docker image
make docker-up       # Start containers
make docker-down     # Stop containers
make docker-logs     # View guardian logs
make docker-clean    # Clean old images/volumes
```

### Local Development Setup

```bash
# Install all dependencies (Python + npm + pre-commit hooks)
make install

# Update all dependencies
make update

# Verify setup
make check
```

**DevContainer:** The `.devcontainer/devcontainer.json` automatically runs:

```json
"postCreateCommand": "pip3 install -e .[dev] && pre-commit install && npm install && npm run prepare"
```

This ensures pre-commit hooks (including `make check`) are active immediately.

### CI/CD Integration

**GitHub Actions Workflows:**

1. **lint.yml**: Runs on all PRs (ruff, mypy, prettier, commitlint)
2. **test.yml**: Runs pytest on all pushes
3. **release.yml**: Semantic-release + Docker build on main branch
4. **docker-publish.yml**: Multi-platform Docker images (amd64, arm64)

**Semantic Versioning:**

- Commits with `feat/fix/perf/refactor/build` trigger releases
- Version tags: `latest`, `X.X.X`, `X.X`, `X` (e.g., v1.5.0 → 1.5.0, 1.5, 1)
- Docker images published to ghcr.io/strausmann/dockhand-guardian

## Agent-Specific Instructions

### When modifying guardian.py:

- Preserve existing configuration options
- Maintain backward compatibility
- Add comprehensive error handling
- Include logging for new operations
- Update type hints

### When modifying Dockerfile:

- Keep image size minimal
- Use official base images
- Pin version numbers
- Clean up in same layer

### When updating documentation:

- Keep README user-focused
- Keep copilot-instructions.md technical/detailed
- Update configuration tables
- Add examples for new features

### When modifying docker-compose.yml:

- Keep example simple
- Show best practices
- Document all options
- Include health checks

## Version History

- **v1.0.0**: Initial release with core monitoring and recovery functionality

## Support

For issues, questions, or contributions, please use the GitHub repository issue tracker.
