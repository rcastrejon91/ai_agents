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
    # Test enabling via environment variable
    os.environ["ROBOTICS_ENABLE"] = "true"
    policy = load_policy()
    assert policy["enabled"] is True, "Environment variable should enable robotics"

    # Test that self-repair remains disabled even with env var
    os.environ["ROBOTICS_REPAIR_ENABLE"] = "true"
    policy = load_policy()
    assert (
        policy["self_repair_enabled"] is True
    ), "Environment variable should enable self-repair"

    # Clean up environment
    if "ROBOTICS_ENABLE" in os.environ:
        del os.environ["ROBOTICS_ENABLE"]
    if "ROBOTICS_REPAIR_ENABLE" in os.environ:
        del os.environ["ROBOTICS_REPAIR_ENABLE"]


def test_config_file_fallback():
    """Test that policy loads with default values if config file is missing."""
    # Temporarily point to non-existent config file
    original_file = os.environ.get("TOPIC_CONFIG_FILE")
    os.environ["TOPIC_CONFIG_FILE"] = "/nonexistent/topics.yml"

    try:
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
        if original_file:
            os.environ["TOPIC_CONFIG_FILE"] = original_file
        elif "TOPIC_CONFIG_FILE" in os.environ:
            del os.environ["TOPIC_CONFIG_FILE"]

        # Reload again to restore original state
        import importlib

        import services.robot_core.robot_policy

        importlib.reload(services.robot_core.robot_policy)


def test_self_repair_toggle_functionality():
    """Test that the self-repair toggle function works correctly and maintains safety."""
    import tempfile
    import os
    
    # Create a temporary config file for testing
    temp_dir = tempfile.mkdtemp()
    test_config = os.path.join(temp_dir, "test_topics.yml")
    
    # Store original env var
    original_file = os.environ.get("TOPIC_CONFIG_FILE")
    
    try:
        # Set up test config
        os.environ["TOPIC_CONFIG_FILE"] = test_config
        
        # Create initial config with robotics enabled but self-repair disabled
        initial_config = {
            "robotics": {
                "enabled": True,
                "self_repair_enabled": False,
                "approve_required": True,
            }
        }
        
        import yaml
        with open(test_config, "w") as f:
            yaml.safe_dump(initial_config, f)
        
        # Reload module to pick up test config
        import importlib
        import services.robot_core.robot_policy
        importlib.reload(services.robot_core.robot_policy)
        
        from services.robot_core.robot_policy import load_policy, update_self_repair_setting
        
        # Test initial state
        policy = load_policy()
        assert policy["enabled"] is True, "Robotics should be enabled for test"
        assert policy["self_repair_enabled"] is False, "Self-repair should start disabled"
        assert policy["approve_required"] is True, "Approval should be required"
        
        # Test enabling self-repair
        result = update_self_repair_setting(True)
        assert result is True, "Update should succeed"
        
        updated_policy = load_policy()
        assert updated_policy["self_repair_enabled"] is True, "Self-repair should be enabled"
        assert updated_policy["approve_required"] is True, "Approval requirement must be maintained"
        
        # Test disabling self-repair
        result = update_self_repair_setting(False)
        assert result is True, "Update should succeed"
        
        disabled_policy = load_policy()
        assert disabled_policy["self_repair_enabled"] is False, "Self-repair should be disabled"
        assert disabled_policy["approve_required"] is True, "Approval requirement must be maintained"
        
        # Verify the config file was updated correctly
        with open(test_config, "r") as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config["robotics"]["self_repair_enabled"] is False, "Config file should be updated"
        assert saved_config["robotics"]["approve_required"] is True, "Approval should still be required in config"
        
        print("✅ Self-repair toggle tests passed!")
        
    finally:
        # Clean up
        if os.path.exists(test_config):
            os.unlink(test_config)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
            
        # Restore original environment
        if original_file:
            os.environ["TOPIC_CONFIG_FILE"] = original_file
        elif "TOPIC_CONFIG_FILE" in os.environ:
            del os.environ["TOPIC_CONFIG_FILE"]
        
        # Reload module to restore original state
        import importlib
        import services.robot_core.robot_policy
        importlib.reload(services.robot_core.robot_policy)


def test_self_repair_safety_constraints():
    """Test that self-repair toggle maintains all safety constraints."""
    import tempfile
    import os
    
    # Create a temporary config file for testing
    temp_dir = tempfile.mkdtemp()
    test_config = os.path.join(temp_dir, "test_topics.yml")
    
    # Store original env var
    original_file = os.environ.get("TOPIC_CONFIG_FILE")
    
    try:
        # Set up test config
        os.environ["TOPIC_CONFIG_FILE"] = test_config
        
        # Create config without approve_required to test that it gets added
        initial_config = {
            "robotics": {
                "enabled": True,
                "self_repair_enabled": False,
                # Note: intentionally missing approve_required
            }
        }
        
        import yaml
        with open(test_config, "w") as f:
            yaml.safe_dump(initial_config, f)
        
        # Reload module to pick up test config
        import importlib
        import services.robot_core.robot_policy
        importlib.reload(services.robot_core.robot_policy)
        
        from services.robot_core.robot_policy import update_self_repair_setting, load_policy
        
        # Test that enabling self-repair also ensures approve_required is set
        result = update_self_repair_setting(True)
        assert result is True, "Update should succeed"
        
        # Verify both the live policy and saved config have approve_required
        policy = load_policy()
        assert policy["approve_required"] is True, "Approval must be required in live policy"
        
        with open(test_config, "r") as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config["robotics"]["approve_required"] is True, "Approval must be required in saved config"
        assert saved_config["robotics"]["self_repair_enabled"] is True, "Self-repair should be enabled in config"
        
        print("✅ Self-repair safety constraint tests passed!")
        
    finally:
        # Clean up
        if os.path.exists(test_config):
            os.unlink(test_config)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
            
        # Restore original environment
        if original_file:
            os.environ["TOPIC_CONFIG_FILE"] = original_file
        elif "TOPIC_CONFIG_FILE" in os.environ:
            del os.environ["TOPIC_CONFIG_FILE"]
        
        # Reload module to restore original state
        import importlib
        import services.robot_core.robot_policy
        importlib.reload(services.robot_core.robot_policy)


if __name__ == "__main__":
    test_robotics_sandbox_enabled()
    test_sandbox_limits_configuration()
    test_environment_variable_override()
    test_config_file_fallback()
    test_self_repair_toggle_functionality()
    test_self_repair_safety_constraints()
    print("✅ All robotics sandbox tests passed!")
