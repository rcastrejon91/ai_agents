import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.robot_core.robot_policy import load_policy


def test_robotics_sandbox_enabled():
    """Test that robotics sandbox is enabled with proper safety measures."""
    policy = load_policy()

    # Verify sandbox is enabled
    assert policy["enabled"] is True, "Robotics sandbox should be enabled"

    # Verify critical safety measures are maintained
    assert policy["approve_required"] is True, "Human approval should be required"
    assert policy["self_repair_enabled"] is False, "Self-repair should be disabled"

    # Verify actuator limits are in place
    assert "actuator_limits" in policy, "Actuator limits should be configured"
    assert (
        policy["actuator_limits"]["max_torque_Nm"] == 2.0
    ), "Torque limit should be 2.0 Nm"
    assert (
        policy["actuator_limits"]["max_speed_mps"] == 0.5
    ), "Speed limit should be 0.5 m/s"

    # Verify materials whitelist
    assert "materials_whitelist" in policy, "Materials whitelist should be configured"
    expected_materials = {"PLA", "PETG", "TPU", "aluminum 6061"}
    assert (
        set(policy["materials_whitelist"]) == expected_materials
    ), "Materials whitelist should match expected"

    # Verify banned terms
    assert "banned_terms" in policy, "Banned terms should be configured"
    expected_banned = {"weapon", "explosive", "lockpick", "chemical dispersal"}
    assert (
        set(policy["banned_terms"]) == expected_banned
    ), "Banned terms should match expected"


def test_sandbox_limits_configuration():
    """Test that sandbox limits are properly configured."""
    policy = load_policy()

    # Verify sandbox_limits section exists
    assert "sandbox_limits" in policy, "Sandbox limits should be configured"

    sandbox_limits = policy["sandbox_limits"]

    # Verify operating area limits
    assert (
        "operating_area" in sandbox_limits
    ), "Operating area limits should be configured"
    assert (
        sandbox_limits["operating_area"]["max_radius_m"] == 50
    ), "Max radius should be 50m"
    assert (
        sandbox_limits["operating_area"]["require_geofence"] is True
    ), "Geofence should be required"

    # Verify session limits
    assert "session_limits" in sandbox_limits, "Session limits should be configured"
    session_limits = sandbox_limits["session_limits"]
    assert (
        session_limits["max_duration_minutes"] == 30
    ), "Max session duration should be 30 minutes"
    assert (
        session_limits["max_operations_per_session"] == 10
    ), "Max operations should be 10 per session"
    assert (
        session_limits["cooldown_between_sessions_minutes"] == 15
    ), "Cooldown should be 15 minutes"

    # Verify monitoring requirements
    assert "monitoring" in sandbox_limits, "Monitoring should be configured"
    monitoring = sandbox_limits["monitoring"]
    assert monitoring["log_all_actions"] is True, "All actions should be logged"
    assert (
        monitoring["video_recording_required"] is True
    ), "Video recording should be required"
    assert (
        monitoring["real_time_telemetry"] is True
    ), "Real-time telemetry should be enabled"
    assert monitoring["alert_on_anomalies"] is True, "Anomaly alerts should be enabled"

    # Verify safety boundaries
    assert (
        "safety_boundaries" in sandbox_limits
    ), "Safety boundaries should be configured"
    safety = sandbox_limits["safety_boundaries"]
    assert (
        safety["emergency_stop_required"] is True
    ), "Emergency stop should be required"
    assert (
        safety["human_supervisor_required"] is True
    ), "Human supervisor should be required"
    assert safety["backup_systems_active"] is True, "Backup systems should be active"


def test_environment_variable_override():
    """Test that environment variables can still override settings."""
    # Store original values for cleanup
    original_robotics_enable = os.environ.get("ROBOTICS_ENABLE")
    original_robotics_repair_enable = os.environ.get("ROBOTICS_REPAIR_ENABLE")
    
    try:
        # Test enabling via environment variable
        os.environ["ROBOTICS_ENABLE"] = "true"
        policy = load_policy()
        assert policy["enabled"] is True, "Environment variable should enable robotics"

        # Test that self-repair can be enabled with env var
        os.environ["ROBOTICS_REPAIR_ENABLE"] = "true"
        policy = load_policy()
        assert (
            policy["self_repair_enabled"] is True
        ), "Environment variable should enable self-repair"
        
    finally:
        # Clean up environment variables
        if original_robotics_enable is not None:
            os.environ["ROBOTICS_ENABLE"] = original_robotics_enable
        elif "ROBOTICS_ENABLE" in os.environ:
            del os.environ["ROBOTICS_ENABLE"]
            
        if original_robotics_repair_enable is not None:
            os.environ["ROBOTICS_REPAIR_ENABLE"] = original_robotics_repair_enable
        elif "ROBOTICS_REPAIR_ENABLE" in os.environ:
            del os.environ["ROBOTICS_REPAIR_ENABLE"]


def test_config_file_fallback():
    """Test that policy loads with default values if config file is missing."""
    # Store original value for cleanup
    original_file = os.environ.get("TOPIC_CONFIG_FILE")
    
    try:
        # Temporarily point to non-existent config file
        os.environ["TOPIC_CONFIG_FILE"] = "/nonexistent/topics.yml"

        # Reload the module to pick up the new environment variable
        import importlib

        import services.robot_core.robot_policy

        importlib.reload(services.robot_core.robot_policy)

        policy = services.robot_core.robot_policy.load_policy()

        # Should fall back to defaults
        assert policy["enabled"] is False, "Should default to disabled"
        assert (
            policy["approve_required"] is True
        ), "Should default to requiring approval"
        assert (
            policy["self_repair_enabled"] is False
        ), "Should default to no self-repair"
        assert (
            "sandbox_limits" not in policy
        ), "Should not have sandbox_limits in defaults"

    finally:
        # Restore original config file
        if original_file is not None:
            os.environ["TOPIC_CONFIG_FILE"] = original_file
        elif "TOPIC_CONFIG_FILE" in os.environ:
            del os.environ["TOPIC_CONFIG_FILE"]

        # Reload again to restore original state
        import importlib

        import services.robot_core.robot_policy

        importlib.reload(services.robot_core.robot_policy)


if __name__ == "__main__":
    test_robotics_sandbox_enabled()
    test_sandbox_limits_configuration()
    test_environment_variable_override()
    test_config_file_fallback()
    print("✅ All robotics sandbox tests passed!")
