# Agents Documentation

This document provides guidance for AI agents working with the Dockhand Guardian project.

## Project Overview

Dockhand Guardian is a Docker sidecar watchdog service that monitors container health and performs automatic recovery. It's designed to be simple, reliable, and require minimal configuration.

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

3. **docker-compose.yml**: Example deployment configuration
   - Shows how to deploy guardian as a sidecar
   - Demonstrates proper volume mounts and networking
   - Includes example monitored services

## Key Design Principles

### 1. Simplicity
- Single Python file for core logic
- Minimal dependencies (docker SDK, requests)
- Configuration via environment variables only

### 2. Safety
- Grace period prevents premature recovery
- Cooldown prevents recovery loops
- Maintenance mode for controlled operations
- Read-only mounts where possible

### 3. Reliability
- Direct Docker socket communication
- Comprehensive error handling
- Detailed logging at all stages
- State tracking to prevent duplicate actions

## Configuration System

All configuration uses environment variables:

```python
self.monitored_containers = os.getenv('MONITORED_CONTAINERS', 'dockhand-app,dockhand-database').split(',')
self.grace_seconds = int(os.getenv('GRACE_SECONDS', '300'))
self.check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
self.cooldown_seconds = int(os.getenv('COOLDOWN_SECONDS', '600'))
```

### Configuration Guidelines
- Always provide sensible defaults
- Use type conversion for numeric values
- Split comma-separated lists for multiple values
- Document all environment variables

## Monitoring Logic

### Health Check Flow

```
1. Check maintenance mode → Skip if active
2. Check cooldown → Skip if in cooldown
3. For each monitored container:
   a. Check Docker container state
   b. Check Docker health status
   c. Check optional HTTP endpoint
4. Track failure times
5. Check if grace period expired
6. Trigger recovery if needed
```

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
```

### Recovery Guidelines
- Always execute both steps
- Log each step clearly
- Reset failure tracking after recovery
- Set cooldown even if recovery fails
- Handle subprocess timeouts

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
  - /var/run/docker.sock:/var/run/docker.sock:ro  # Docker API access
  - .:/stack:ro  # Stack directory for compose commands
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
2. **Alerting**: Webhook notifications for recovery events
3. **Dashboard**: Simple web UI for status
4. **Multiple Stacks**: Support monitoring multiple compose stacks
5. **Custom Scripts**: Run custom scripts pre/post recovery
6. **Health Check Plugins**: Plugin system for custom health checks

## Contributing Guidelines

When contributing:
1. Maintain backward compatibility
2. Add tests for new features
3. Update documentation
4. Follow existing code style
5. Add logging for new operations
6. Handle errors gracefully

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
- Keep Agents.md technical/detailed
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
