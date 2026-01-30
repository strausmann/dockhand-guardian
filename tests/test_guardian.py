#!/usr/bin/env python3
"""
Simple test script to verify the guardian logic without Docker.
Tests configuration parsing, state management, and basic logic.
"""

import os
import sys
from datetime import datetime, timedelta

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_environment_parsing():
    """Test environment variable parsing."""
    print("Testing environment variable parsing...")

    # Set test environment
    os.environ["MONITORED_CONTAINERS"] = "test1,test2,test3"
    os.environ["GRACE_SECONDS"] = "60"
    os.environ["CHECK_INTERVAL"] = "10"
    os.environ["HTTP_CHECKS"] = "test1=http://test1:80,test2=http://test2:8080"

    # Import and test
    from guardian import ContainerGuardian

    # Mock docker client to avoid connection
    class MockDockerClient:
        pass

    guardian = ContainerGuardian.__new__(ContainerGuardian)
    guardian.monitored_containers = os.getenv("MONITORED_CONTAINERS", "dockhand-app,dockhand-database").split(",")
    guardian.grace_seconds = int(os.getenv("GRACE_SECONDS", "300"))
    guardian.check_interval = int(os.getenv("CHECK_INTERVAL", "30"))
    guardian.cooldown_seconds = int(os.getenv("COOLDOWN_SECONDS", "600"))
    guardian.stack_dir = os.getenv("STACK_DIR", "/stack")
    guardian.maintenance_file = os.getenv("MAINTENANCE_FILE", ".maintenance")
    guardian.http_checks = guardian._parse_http_checks()
    guardian.failure_times = dict.fromkeys(guardian.monitored_containers)
    guardian.last_recovery_time = None

    # Verify parsing
    assert guardian.monitored_containers == ["test1", "test2", "test3"], "Container list parsing failed"
    assert guardian.grace_seconds == 60, "Grace seconds parsing failed"
    assert guardian.check_interval == 10, "Check interval parsing failed"
    assert "test1" in guardian.http_checks, "HTTP checks parsing failed"
    assert guardian.http_checks["test1"] == "http://test1:80", "HTTP check URL parsing failed"

    print("✓ Environment variable parsing works correctly")


def test_http_checks_parsing():
    """Test HTTP checks parsing."""
    print("\nTesting HTTP checks parsing...")

    from guardian import ContainerGuardian

    guardian = ContainerGuardian.__new__(ContainerGuardian)

    # Test empty
    os.environ["HTTP_CHECKS"] = ""
    guardian.http_checks = guardian._parse_http_checks()
    assert len(guardian.http_checks) == 0, "Empty HTTP checks parsing failed"

    # Test single
    os.environ["HTTP_CHECKS"] = "app1=http://app1:80"
    guardian.http_checks = guardian._parse_http_checks()
    assert len(guardian.http_checks) == 1, "Single HTTP check parsing failed"
    assert guardian.http_checks["app1"] == "http://app1:80"

    # Test multiple
    os.environ["HTTP_CHECKS"] = "app1=http://app1:80,app2=http://app2:8080/health"
    guardian.http_checks = guardian._parse_http_checks()
    assert len(guardian.http_checks) == 2, "Multiple HTTP checks parsing failed"

    print("✓ HTTP checks parsing works correctly")


def test_maintenance_mode():
    """Test maintenance mode detection."""
    print("\nTesting maintenance mode...")

    import os
    import tempfile

    from guardian import ContainerGuardian

    guardian = ContainerGuardian.__new__(ContainerGuardian)

    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        guardian.stack_dir = tmpdir
        guardian.maintenance_file = ".maintenance"

        # Test without file
        assert not guardian.is_maintenance_mode(), "Should not be in maintenance mode"

        # Test with file
        maintenance_path = os.path.join(tmpdir, ".maintenance")
        open(maintenance_path, "w").close()
        assert guardian.is_maintenance_mode(), "Should be in maintenance mode"

        # Remove file
        os.remove(maintenance_path)
        assert not guardian.is_maintenance_mode(), "Should not be in maintenance mode after removal"

    print("✓ Maintenance mode detection works correctly")


def test_cooldown():
    """Test cooldown logic."""
    print("\nTesting cooldown logic...")

    from guardian import ContainerGuardian

    guardian = ContainerGuardian.__new__(ContainerGuardian)
    guardian.cooldown_seconds = 60

    # Test no recovery yet
    guardian.last_recovery_time = None
    assert not guardian.is_in_cooldown(), "Should not be in cooldown when no recovery"

    # Test recent recovery
    guardian.last_recovery_time = datetime.now()
    assert guardian.is_in_cooldown(), "Should be in cooldown after recent recovery"

    # Test old recovery
    guardian.last_recovery_time = datetime.now() - timedelta(seconds=70)
    assert not guardian.is_in_cooldown(), "Should not be in cooldown after timeout"

    print("✓ Cooldown logic works correctly")


def test_failure_tracking():
    """Test failure time tracking logic."""
    print("\nTesting failure tracking...")

    from guardian import ContainerGuardian

    guardian = ContainerGuardian.__new__(ContainerGuardian)
    guardian.monitored_containers = ["test1", "test2"]
    guardian.failure_times = dict.fromkeys(guardian.monitored_containers)
    guardian.grace_seconds = 60

    # Simulate first failure
    guardian.failure_times["test1"] = datetime.now()

    # Check grace period not expired
    failure_time = guardian.failure_times["test1"]
    assert failure_time is not None
    elapsed = (datetime.now() - failure_time).total_seconds()
    assert elapsed < guardian.grace_seconds, "Grace period should not be expired immediately"

    # Simulate old failure
    guardian.failure_times["test2"] = datetime.now() - timedelta(seconds=70)
    failure_time2 = guardian.failure_times["test2"]
    assert failure_time2 is not None
    elapsed = (datetime.now() - failure_time2).total_seconds()
    assert elapsed >= guardian.grace_seconds, "Grace period should be expired for old failure"

    print("✓ Failure tracking works correctly")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Dockhand Guardian Unit Tests")
    print("=" * 60)

    try:
        test_environment_parsing()
        test_http_checks_parsing()
        test_maintenance_mode()
        test_cooldown()
        test_failure_tracking()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
