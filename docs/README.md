# 🛡️ Dockhand Guardian

[![Release](https://img.shields.io/github/v/release/strausmann/dockhand-guardian)](https://github.com/strausmann/dockhand-guardian/releases)
[![License](https://img.shields.io/github/license/strausmann/dockhand-guardian)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Semantic Release](https://img.shields.io/badge/semantic--release-enabled-brightgreen)](https://github.com/semantic-release/semantic-release)
[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/)

A Docker sidecar watchdog that monitors container health and automatically recovers failed
containers without requiring an external API.

> [!NOTE] This project is **not officially part of the Dockhand project** and is maintained
> independently.

> [!TIP] 🤖 **AI-Assisted Development**: This project is developed with assistance from GitHub
> Copilot, leveraging AI to enhance code quality and development efficiency.

## 📋 Overview

Dockhand Guardian is a lightweight Python-based monitoring service that watches over your Docker
containers (specifically `dockhand-app` and `dockhand-database`) via Docker socket. When containers
fail health checks for longer than a configured grace period, it automatically triggers a recovery
process by pulling the latest images and recreating the containers.

## 📁 Project Structure

```
dockhand-guardian/
├── src/                    # Application source code
│   ├── __init__.py
│   └── guardian.py         # Main watchdog application
│
├── tests/                  # Unit tests
│   └── test_guardian.py
│
├── docker/                 # Docker & container configuration
│   ├── Dockerfile          # Container image definition
│   └── docker-compose.yml  # Example deployment setup
│
├── docs/                   # Documentation
│   ├── README.md           # This file
│   ├── CONTRIBUTING.md     # Contribution guidelines
│   ├── WEBHOOKS.md         # Webhook configuration guide
│   └── CHANGELOG.md        # Version history
│
├── .github/                # GitHub configuration
│   ├── workflows/          # CI/CD workflows
│   ├── ISSUE_TEMPLATE/     # Issue templates
│   └── dependabot.yml      # Dependency automation
│
└── Root files              # Config & symlinks
    ├── pyproject.toml      # Python dependencies & project config
    ├── package.json        # npm dev tools
    ├── Makefile            # Development commands
    └── .releaserc.json     # Release automation
```

> **Note:** Important files (README, Dockerfile, docker-compose.yml, CHANGELOG) are symlinked to the
> root for convenience and GitHub compatibility.

## ✨ Features

- 🔍 **Container Health Monitoring**: Monitors Docker container state and built-in health checks
- 🌐 **Optional HTTP Checks**: Additional HTTP endpoint health verification
- ⏱️ **Grace Period**: Configurable grace period before triggering recovery
- 🔄 **Auto-Recovery**: Automatically pulls latest images and recreates containers
- 🔧 **Maintenance Mode**: Support for maintenance flag file to pause monitoring
- ⏸️ **Cooldown Period**: Prevents recovery loops with configurable cooldown
- 🐳 **Docker Socket Communication**: Direct communication with Docker daemon (no external API
  needed)
- 📢 **Webhook Notifications**: Send alerts via 80+ services using Apprise (Discord, Teams, Slack,
  Email, etc.)
- ⚙️ **Configurable**: All parameters configurable via environment variables

## 🚀 Quick Start

### Using Pre-built Docker Image

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/strausmann/dockhand-guardian:latest

# Or use specific version
docker pull ghcr.io/strausmann/dockhand-guardian:1.4.1  # Full version
docker pull ghcr.io/strausmann/dockhand-guardian:1.4    # Minor version
docker pull ghcr.io/strausmann/dockhand-guardian:1      # Major version

# Or use in docker-compose.yml
services:
  guardian:
    image: ghcr.io/strausmann/dockhand-guardian:latest
    # ... rest of configuration
```

### Building from Source

1. **Clone the repository**:

   ```bash
   git clone https://github.com/strausmann/dockhand-guardian.git
   cd dockhand-guardian
   ```

2. **Build and start the stack**:

   ```bash
   docker compose up -d
   ```

3. **View guardian logs**:
   ```bash
   docker compose logs -f guardian
   ```

## 📋 Usage Examples

### Deployment Architecture

> [!TIP] **Recommended:** Run the guardian in a **separate stack** from the monitored containers.
> This ensures the guardian remains running during recovery operations and can monitor multiple
> stacks.

> [!NOTE] **Alternative:** You can run the guardian in the same stack as the monitored containers,
> but be aware that it will be briefly restarted during recovery operations when
> `docker compose up -d --force-recreate` is executed.

### Docker CLI (Separate Stack - Recommended)

Run guardian as a standalone container monitoring another stack:

```bash
docker run -d \
  --name dockhand-guardian \
  --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v "/path/to/monitored/stack:/stack:ro" \
  -e MONITORED_CONTAINERS=dockhand-app,dockhand-database \
  -e GRACE_SECONDS=300 \
  -e CHECK_INTERVAL=30 \
  -e COOLDOWN_SECONDS=600 \
  -e HTTP_CHECKS=dockhand-app=http://dockhand-app:80/health \
  -e WEBHOOK_URLS=discord://webhook_id/token \
  ghcr.io/strausmann/dockhand-guardian:latest
```

### Docker Compose (Separate Stack - Recommended)

**Guardian Stack** (`guardian/docker-compose.yml`):

```yaml
services:
  guardian:
    image: ghcr.io/strausmann/dockhand-guardian:latest
    container_name: dockhand-guardian
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /path/to/monitored/stack:/stack:ro
    environment:
      MONITORED_CONTAINERS: dockhand-app,dockhand-database
      GRACE_SECONDS: 300
      CHECK_INTERVAL: 30
      COOLDOWN_SECONDS: 600
```

**Monitored Stack** (`app/docker-compose.yml`):

```yaml
services:
  dockhand-app:
    image: nginx:alpine
    container_name: dockhand-app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3

  dockhand-database:
    image: postgres:16-alpine
    container_name: dockhand-database
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
```

### Docker Compose (Same Stack - Alternative)

**Single Stack** (guardian monitors containers in same compose file):

### Docker Compose (Same Stack - Alternative)

**Single Stack** (guardian monitors containers in same compose file):

> [!WARNING] When using this approach, the guardian will be restarted during recovery operations.
> Monitoring will be interrupted for a few seconds while the guardian restarts.

```yaml
services:
  dockhand-app:
    image: nginx:alpine
    container_name: dockhand-app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  dockhand-database:
    image: postgres:16-alpine
    container_name: dockhand-database
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: example
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  guardian:
    image: ghcr.io/strausmann/dockhand-guardian:latest
    container_name: dockhand-guardian
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - .:/stack:ro
    environment:
      MONITORED_CONTAINERS: dockhand-app,dockhand-database
      GRACE_SECONDS: 300
      CHECK_INTERVAL: 30
      COOLDOWN_SECONDS: 600
      HTTP_CHECKS: dockhand-app=http://dockhand-app:80/
      WEBHOOK_URLS: discord://webhook_id/token
```

**Using Docker Compose Secrets:**

```yaml
services:
  guardian:
    image: ghcr.io/strausmann/dockhand-guardian:latest
    container_name: dockhand-guardian
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - .:/stack:ro
    environment:
      MONITORED_CONTAINERS: dockhand-app,dockhand-database
      GRACE_SECONDS: 300
      WEBHOOK_URLS_FILE: /run/secrets/webhook_urls
    secrets:
      - webhook_urls

secrets:
  webhook_urls:
    file: ./secrets/webhook_urls.txt
```

## ⚙️ Configuration

All configuration is done via environment variables:

| Variable               | Description                                                    | Default                          |
| ---------------------- | -------------------------------------------------------------- | -------------------------------- |
| `MONITORED_CONTAINERS` | Comma-separated list of container names to monitor             | `dockhand-app,dockhand-database` |
| `GRACE_SECONDS`        | Time in seconds to wait before triggering recovery             | `300`                            |
| `CHECK_INTERVAL`       | How often to check container health (seconds)                  | `30`                             |
| `COOLDOWN_SECONDS`     | Cooldown period after recovery (seconds)                       | `600`                            |
| `STACK_DIR`            | Directory containing docker-compose.yml                        | `/stack`                         |
| `MAINTENANCE_FILE`     | Maintenance mode flag file name                                | `.maintenance`                   |
| `HTTP_CHECKS`          | Optional HTTP checks (format: `container=url,container2=url2`) | _(empty)_                        |
| `WEBHOOK_URLS`         | Webhook URLs for notifications (comma-separated Apprise URLs)  | _(empty)_                        |

### Example Configuration

```yaml
environment:
  MONITORED_CONTAINERS: dockhand-app,dockhand-database
  GRACE_SECONDS: 300
  CHECK_INTERVAL: 30
  COOLDOWN_SECONDS: 600
  HTTP_CHECKS: dockhand-app=http://dockhand-app:80/health
```

## 📢 Webhook Notifications

Guardian uses [Apprise](https://github.com/caronc/apprise) for webhook notifications, supporting 80+
notification services including Discord, Microsoft Teams, Slack, Telegram, Email, and many more.

### Quick Setup

Configure notifications via Apprise URLs:

```yaml
environment:
  # Single service
  WEBHOOK_URLS: discord://webhook_id/webhook_token

  # Multiple services (comma-separated)
  WEBHOOK_URLS: discord://webhook_id/token,mailto://user:pass@gmail.com
```

### Discord

1. Create webhook in Discord:
   - Server Settings → Integrations → Webhooks → New Webhook
   - Copy webhook URL: `https://discord.com/api/webhooks/ID/TOKEN`

2. Configure guardian:
   ```yaml
   WEBHOOK_URLS: discord://webhook_id/webhook_token
   ```

### Microsoft Teams

1. Create webhook in Teams:
   - Channel → Connectors → Incoming Webhook
   - Copy webhook URL

2. Configure guardian:
   ```yaml
   WEBHOOK_URLS: msteams://TokenA/TokenB/TokenC/
   ```

### Slack

1. Create Slack App with incoming webhook
2. Configure guardian:
   ```yaml
   WEBHOOK_URLS: slack://TokenA/TokenB/TokenC/
   ```

### Multiple Services

Send notifications to multiple services simultaneously:

```yaml
WEBHOOK_URLS: discord://ID/TOKEN,msteams://A/B/C/,slack://X/Y/Z/
```

### More Services

Apprise supports 80+ services. See [Apprise documentation](https://github.com/caronc/apprise/wiki)
for all supported URLs:

- Email (SMTP, Gmail, etc.)
- Telegram
- Matrix
- Pushover
- IFTTT
- Custom JSON endpoints
- And many more!

## 🔧 Maintenance Mode

To pause monitoring during maintenance:

```bash
# Enable maintenance mode
touch .maintenance

# Disable maintenance mode
rm .maintenance
```

When the maintenance file exists in the stack directory, the guardian will skip all health checks.

## 🔄 How It Works

1. **Monitoring**: Guardian checks each monitored container every `CHECK_INTERVAL` seconds
2. **Health Checks**:
   - Verifies container is running
   - Checks Docker health status (if configured)
   - Optionally checks HTTP endpoints
3. **Grace Period**: If a container fails checks, guardian waits `GRACE_SECONDS` before taking
   action
4. **Recovery**: After grace period expires:
   - Executes `docker compose pull` to get latest images
   - Executes `docker compose up -d --force-recreate` to recreate containers
5. **Cooldown**: After recovery, waits `COOLDOWN_SECONDS` before monitoring again

## 📦 Docker Compose Example

See [docker-compose.yml](docker-compose.yml) for a complete example including:

- Sample application container (nginx)
- Sample database container (PostgreSQL)
- Guardian sidecar configuration
- Proper volume mounts and networking

## 🏗️ Building the Image

```bash
# Local build
docker build -t dockhand-guardian .

# Multi-platform build (amd64 + arm64)
docker buildx build --platform linux/amd64,linux/arm64 -t dockhand-guardian .
```

Docker images are automatically built and published to
[GitHub Container Registry](https://github.com/strausmann/dockhand-guardian/pkgs/container/dockhand-guardian)
on every release with semantic version tags:

- `latest` - Always points to the newest release
- `X.X.X` - Full version (e.g., `1.4.1`)
- `X.X` - Minor version, updated with patches (e.g., `1.4`)
- `X` - Major version, updated with minor/patch (e.g., `1`)

## 💻 Development

### Requirements

- Python 3.11+
- Docker
- Docker Compose

### Setup

```bash
# Install dependencies (includes dev tools)
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Code Quality Tools

This project uses modern Python tooling:

- **[Ruff](https://docs.astral.sh/ruff/)**: Ultra-fast linter and formatter (10-100x faster than
  flake8/black/isort)
- **[mypy](https://mypy-lang.org/)**: Static type checking
- **[pre-commit](https://pre-commit.com/)**: Automated Git hooks for code quality
- **[pytest](https://pytest.org/)**: Testing framework with coverage reporting

```bash
# Lint code
make lint              # Run ruff checks

# Format code
make format            # Auto-fix issues and format

# Type check
make type-check        # Run mypy

# Run tests
make test              # Run pytest with coverage

# Run all checks
make check             # Lint + format-check + type-check + tests

# Git workflow
make commit            # Interactive commit with quality checks
make amend             # Add changes to last commit
make push              # Pull with rebase and push
```

### Running Locally

```bash
# Set environment variables
export MONITORED_CONTAINERS=dockhand-app,dockhand-database
export GRACE_SECONDS=60
export STACK_DIR=/path/to/your/stack

# Run guardian
python src/guardian.py
```

### Contributing Guidelines

This project uses semantic versioning and conventional commits:

```bash
# Install dependencies
npm install

# Make changes and commit using commitizen
npm run commit

# Or commit manually with proper format
git commit -m "feat(monitoring): add new health check type"
```

Pre-commit hooks will automatically:

- Run Ruff linting and formatting
- Check type hints with mypy
- Validate YAML files
- Run tests

See [SCOPES.md](.github/SCOPES.md) for available commit scopes.

## 🔒 Security Considerations

- The guardian requires read access to Docker socket (`/var/run/docker.sock`)
- Mount the stack directory as read-only (`:ro`) when possible
- Use Docker secrets for sensitive configuration in production
- The guardian has permission to recreate containers, so protect access appropriately

## 🔍 Troubleshooting

### Guardian not detecting containers

- Verify container names match exactly (check with `docker ps`)
- Ensure containers are in the same Docker network
- Check guardian logs: `docker compose logs guardian`

### Recovery not triggering

- Check if maintenance mode is enabled (`.maintenance` file exists)
- Verify grace period has elapsed
- Check if in cooldown period after previous recovery
- Review guardian logs for error messages

### Permission denied errors

- Ensure Docker socket is properly mounted
- Verify guardian has access to stack directory
- Check Docker socket permissions on host

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! This project uses:

- 📝 [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning
- 🔄 [Semantic Release](https://github.com/semantic-release/semantic-release) for automated releases
- 🐳 Automatic Docker image publishing to GitHub Container Registry
- 🎯 Required commit scopes (see [SCOPES.md](.github/SCOPES.md))

**Important:** Not all commits trigger releases:

- ✅ `feat`, `fix`, `perf`, `refactor`, `build` → **Create releases + Docker images**
- ⏸️ `docs`, `ci`, `test`, `style`, `chore` → **No release** (documentation & tooling only)

**Dependency Updates:**

- 🐳 Docker base image updates → **Automatic patch release + new Docker image**
- 🐍 Python package updates → **Automatic patch release + new Docker image**
- ⚙️ GitHub Actions updates → **No release** (CI tooling only)
- 📦 npm updates → **No release** (dev tooling only)

For detailed guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## 👤 Author

Björn Strausmann
