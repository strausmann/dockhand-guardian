# Dockhand Guardian

A Docker sidecar watchdog that monitors container health and automatically recovers failed containers without requiring an external API.

## Overview

Dockhand Guardian is a lightweight Python-based monitoring service that watches over your Docker containers (specifically `dockhand-app` and `dockhand-database`) via Docker socket. When containers fail health checks for longer than a configured grace period, it automatically triggers a recovery process by pulling the latest images and recreating the containers.

## Features

- **Container Health Monitoring**: Monitors Docker container state and built-in health checks
- **Optional HTTP Checks**: Additional HTTP endpoint health verification
- **Grace Period**: Configurable grace period before triggering recovery
- **Auto-Recovery**: Automatically pulls latest images and recreates containers
- **Maintenance Mode**: Support for maintenance flag file to pause monitoring
- **Cooldown Period**: Prevents recovery loops with configurable cooldown
- **Docker Socket Communication**: Direct communication with Docker daemon (no external API needed)
- **Configurable**: All parameters configurable via environment variables

## Quick Start

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

## Configuration

All configuration is done via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MONITORED_CONTAINERS` | Comma-separated list of container names to monitor | `dockhand-app,dockhand-database` |
| `GRACE_SECONDS` | Time in seconds to wait before triggering recovery | `300` |
| `CHECK_INTERVAL` | How often to check container health (seconds) | `30` |
| `COOLDOWN_SECONDS` | Cooldown period after recovery (seconds) | `600` |
| `STACK_DIR` | Directory containing docker-compose.yml | `/stack` |
| `MAINTENANCE_FILE` | Maintenance mode flag file name | `.maintenance` |
| `HTTP_CHECKS` | Optional HTTP checks (format: `container=url,container2=url2`) | _(empty)_ |

### Example Configuration

```yaml
environment:
  MONITORED_CONTAINERS: dockhand-app,dockhand-database
  GRACE_SECONDS: 300
  CHECK_INTERVAL: 30
  COOLDOWN_SECONDS: 600
  HTTP_CHECKS: dockhand-app=http://dockhand-app:80/health
```

## Maintenance Mode

To pause monitoring during maintenance:

```bash
# Enable maintenance mode
touch .maintenance

# Disable maintenance mode
rm .maintenance
```

When the maintenance file exists in the stack directory, the guardian will skip all health checks.

## How It Works

1. **Monitoring**: Guardian checks each monitored container every `CHECK_INTERVAL` seconds
2. **Health Checks**:
   - Verifies container is running
   - Checks Docker health status (if configured)
   - Optionally checks HTTP endpoints
3. **Grace Period**: If a container fails checks, guardian waits `GRACE_SECONDS` before taking action
4. **Recovery**: After grace period expires:
   - Executes `docker compose pull` to get latest images
   - Executes `docker compose up -d --force-recreate` to recreate containers
5. **Cooldown**: After recovery, waits `COOLDOWN_SECONDS` before monitoring again

## Docker Compose Example

See [docker-compose.yml](docker-compose.yml) for a complete example including:
- Sample application container (nginx)
- Sample database container (PostgreSQL)
- Guardian sidecar configuration
- Proper volume mounts and networking

## Building the Image

```bash
docker build -t dockhand-guardian .
```

## Development

### Requirements

- Python 3.11+
- Docker
- Docker Compose

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MONITORED_CONTAINERS=dockhand-app,dockhand-database
export GRACE_SECONDS=60
export STACK_DIR=/path/to/your/stack

# Run guardian
python guardian.py
```

## Security Considerations

- The guardian requires read access to Docker socket (`/var/run/docker.sock`)
- Mount the stack directory as read-only (`:ro`) when possible
- Use Docker secrets for sensitive configuration in production
- The guardian has permission to recreate containers, so protect access appropriately

## Troubleshooting

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

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Björn Strausmann