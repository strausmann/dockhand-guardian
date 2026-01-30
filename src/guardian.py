#!/usr/bin/env python3
"""
Dockhand Guardian - Docker Sidecar Watchdog
Monitors dockhand-app and dockhand-database containers via docker.sock
and performs automatic recovery when health checks fail.
"""

import os
import sys
import time
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
import docker
import requests
import apprise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('guardian')


class ContainerGuardian:
    """Main guardian class that monitors and recovers containers."""

    def __init__(self):
        # Configuration from environment variables
        self.monitored_containers = os.getenv('MONITORED_CONTAINERS', 'dockhand-app,dockhand-database').split(',')
        self.grace_seconds = int(os.getenv('GRACE_SECONDS', '300'))
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
        self.cooldown_seconds = int(os.getenv('COOLDOWN_SECONDS', '600'))
        self.stack_dir = os.getenv('STACK_DIR', '/stack')
        self.maintenance_file = os.getenv('MAINTENANCE_FILE', '.maintenance')
        self.http_checks = self._parse_http_checks()

        # Webhook configuration via Apprise
        self.webhook_urls = os.getenv('WEBHOOK_URLS', '').strip()
        self.webhook_enabled = bool(self.webhook_urls)

        # Initialize Apprise
        self.apprise = apprise.Apprise()
        if self.webhook_enabled:
            for url in self.webhook_urls.split(','):
                url = url.strip()
                if url:
                    self.apprise.add(url)

        # State tracking
        self.failure_times: Dict[str, Optional[datetime]] = {name: None for name in self.monitored_containers}
        self.last_recovery_time: Optional[datetime] = None

        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            sys.exit(1)

        logger.info("Guardian initialized with config:")
        logger.info(f"  Monitored containers: {self.monitored_containers}")
        logger.info(f"  Grace period: {self.grace_seconds}s")
        logger.info(f"  Check interval: {self.check_interval}s")
        logger.info(f"  Cooldown: {self.cooldown_seconds}s")
        logger.info(f"  Stack directory: {self.stack_dir}")
        logger.info(f"  HTTP checks: {len(self.http_checks)} configured")
        webhook_status = (
            f"enabled ({len(self.apprise)} service(s))" if self.webhook_enabled
            else "disabled"
        )
        logger.info(f"  Webhook notifications: {webhook_status}")

    def _parse_http_checks(self) -> Dict[str, str]:
        """Parse HTTP_CHECKS environment variable.
        Format: container1=http://url1,container2=http://url2
        """
        http_checks = {}
        http_checks_str = os.getenv('HTTP_CHECKS', '')
        if http_checks_str:
            for check in http_checks_str.split(','):
                if '=' in check:
                    container, url = check.split('=', 1)
                    http_checks[container.strip()] = url.strip()
        return http_checks

    def send_webhook_notification(self, containers: List[str], success: bool):
        """Send webhook notification about recovery action via Apprise.

        Args:
            containers: List of container names that triggered recovery
            success: Whether the recovery was successful
        """
        if not self.webhook_enabled:
            return

        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            status_emoji = "✅" if success else "❌"
            status_text = "Recovery Successful" if success else "Recovery Failed"

            title = f"{status_emoji} Dockhand Guardian Alert"
            body = f"**{status_text}**\n\n" \
                   f"🐳 **Affected Containers:**\n" + \
                   '\n'.join([f"  • {c}" for c in containers]) + \
                   f"\n\n⏰ **Timestamp:** {timestamp}"

            # Send notification via Apprise
            result = self.apprise.notify(
                title=title,
                body=body
            )

            if result:
                logger.info(f"Webhook notification sent successfully to {len(self.apprise)} service(s)")
            else:
                logger.warning("Webhook notification failed for some or all services")

        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")

    def is_maintenance_mode(self) -> bool:
        """Check if maintenance mode is active."""
        maintenance_path = os.path.join(self.stack_dir, self.maintenance_file)
        is_maintenance = os.path.exists(maintenance_path)
        if is_maintenance:
            logger.debug("Maintenance mode is active")
        return is_maintenance

    def is_in_cooldown(self) -> bool:
        """Check if we're in cooldown period after last recovery."""
        if self.last_recovery_time is None:
            return False

        elapsed = (datetime.now() - self.last_recovery_time).total_seconds()
        in_cooldown = elapsed < self.cooldown_seconds

        if in_cooldown:
            remaining = self.cooldown_seconds - elapsed
            logger.debug(f"In cooldown period: {remaining:.0f}s remaining")

        return in_cooldown

    def check_container_health(self, container_name: str) -> bool:
        """Check if a container is healthy.
        Returns True if healthy, False otherwise.
        """
        try:
            # Try to find the container
            containers = self.docker_client.containers.list(
                all=True,
                filters={'name': container_name}
            )

            if not containers:
                logger.warning(f"Container '{container_name}' not found")
                return False

            container = containers[0]

            # Check if container is running
            if container.status != 'running':
                logger.warning(f"Container '{container_name}' is not running (status: {container.status})")
                return False

            # Check Docker health status if available
            container.reload()  # Refresh container info
            health = container.attrs.get('State', {}).get('Health', {})

            if health:
                health_status = health.get('Status', 'unknown')
                if health_status == 'healthy':
                    logger.debug(f"Container '{container_name}' is healthy (Docker health check)")
                    return True
                elif health_status in ['unhealthy', 'starting']:
                    logger.warning(f"Container '{container_name}' health status: {health_status}")
                    return False
            else:
                # No health check defined, consider it healthy if running
                logger.debug(f"Container '{container_name}' is running (no health check defined)")
                return True

            return True

        except Exception as e:
            logger.error(f"Error checking container '{container_name}': {e}")
            return False

    def check_http_endpoint(self, container_name: str) -> bool:
        """Check HTTP endpoint if configured for this container.
        Returns True if check passes or not configured, False if check fails.
        """
        if container_name not in self.http_checks:
            return True  # No HTTP check configured, pass by default

        url = self.http_checks[container_name]
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                logger.debug(f"HTTP check passed for '{container_name}': {url}")
                return True
            else:
                logger.warning(f"HTTP check failed for '{container_name}': {url} returned {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"HTTP check failed for '{container_name}': {url} - {e}")
            return False

    def check_container(self, container_name: str) -> bool:
        """Perform all checks for a container.
        Returns True if all checks pass, False otherwise.
        """
        # Check Docker container health
        container_healthy = self.check_container_health(container_name)
        if not container_healthy:
            return False

        # Check HTTP endpoint if configured
        http_healthy = self.check_http_endpoint(container_name)
        if not http_healthy:
            return False

        return True

    def recover_stack(self):
        """Perform recovery by pulling and recreating containers."""
        logger.warning("=" * 60)
        logger.warning("INITIATING STACK RECOVERY")
        logger.warning("=" * 60)

        recovery_success = False
        failed_containers = [name for name, time in self.failure_times.items() if time is not None]

        try:
            # Change to stack directory
            os.chdir(self.stack_dir)

            # Step 1: Pull latest images
            logger.info("Step 1: Pulling latest images...")
            result = subprocess.run(
                ['docker', 'compose', 'pull'],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                logger.error(f"docker compose pull failed: {result.stderr}")
            else:
                logger.info("Images pulled successfully")

            # Step 2: Recreate containers
            logger.info("Step 2: Recreating containers...")
            result = subprocess.run(
                ['docker', 'compose', 'up', '-d', '--force-recreate'],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                logger.error(f"docker compose up failed: {result.stderr}")
                raise Exception("Recovery failed")
            else:
                logger.info("Containers recreated successfully")
                recovery_success = True

            # Update recovery time and reset failure tracking
            self.last_recovery_time = datetime.now()
            for container_name in self.monitored_containers:
                self.failure_times[container_name] = None

            logger.warning("=" * 60)
            logger.warning("STACK RECOVERY COMPLETED")
            logger.warning("=" * 60)

        except Exception as e:
            logger.error(f"Recovery failed with error: {e}")
            self.last_recovery_time = datetime.now()  # Set cooldown even on failure
        finally:
            # Send webhook notification
            self.send_webhook_notification(failed_containers, recovery_success)

    def monitor_containers(self):
        """Main monitoring loop."""
        logger.info("Starting container monitoring...")

        while True:
            try:
                # Check if in maintenance mode
                if self.is_maintenance_mode():
                    logger.debug("Skipping checks: maintenance mode active")
                    time.sleep(self.check_interval)
                    continue

                # Check if in cooldown
                if self.is_in_cooldown():
                    logger.debug("Skipping checks: in cooldown period")
                    time.sleep(self.check_interval)
                    continue

                # Check each monitored container
                containers_needing_recovery = []

                for container_name in self.monitored_containers:
                    is_healthy = self.check_container(container_name)

                    if is_healthy:
                        # Container is healthy, reset failure time
                        if self.failure_times[container_name] is not None:
                            logger.info(f"Container '{container_name}' recovered")
                            self.failure_times[container_name] = None
                    else:
                        # Container is unhealthy
                        if self.failure_times[container_name] is None:
                            # First failure detected
                            self.failure_times[container_name] = datetime.now()
                            logger.warning(f"Container '{container_name}' failure detected, grace period started")
                        else:
                            # Check if grace period has expired
                            elapsed = (datetime.now() - self.failure_times[container_name]).total_seconds()
                            if elapsed >= self.grace_seconds:
                                logger.warning(f"Container '{container_name}' grace period expired ({elapsed:.0f}s)")
                                containers_needing_recovery.append(container_name)
                            else:
                                remaining = self.grace_seconds - elapsed
                                logger.info(
                                    f"Container '{container_name}' unhealthy for {elapsed:.0f}s "
                                    f"(grace: {remaining:.0f}s remaining)"
                                )

                # Perform recovery if any container needs it
                if containers_needing_recovery:
                    logger.warning(f"Recovery needed for: {', '.join(containers_needing_recovery)}")
                    self.recover_stack()
                else:
                    logger.debug("All monitored containers are healthy")

            except KeyboardInterrupt:
                logger.info("Shutdown signal received")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)

            # Wait before next check
            time.sleep(self.check_interval)

        logger.info("Guardian shutdown complete")


def main():
    """Main entry point."""
    logger.info("Dockhand Guardian starting...")

    guardian = ContainerGuardian()
    guardian.monitor_containers()


if __name__ == '__main__':
    main()
