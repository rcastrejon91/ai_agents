import logging
import os

import yaml

TOPIC_CONFIG_FILE = os.getenv("TOPIC_CONFIG_FILE", "topics.yml")
DEFAULT = {
    "enabled": False,
    "self_repair_enabled": False,
    "approve_required": True,
    "banned_terms": ["weapon", "explosive", "lockpick", "chemical dispersal"],
    "materials_whitelist": ["PLA", "PETG", "TPU", "aluminum 6061"],
    "actuator_limits": {"max_torque_Nm": 2.0, "max_speed_mps": 0.5},
}


def validate_sandbox_limits(sandbox_limits):
    """Validate that sandbox_limits contains all required safety parameters."""
    if not isinstance(sandbox_limits, dict):
        raise ValueError("sandbox_limits must be a dictionary")
    
    required_sections = {
        "operating_area": ["max_radius_m", "require_geofence"],
        "session_limits": ["max_duration_minutes", "max_operations_per_session", "cooldown_between_sessions_minutes"],
        "monitoring": ["log_all_actions", "video_recording_required", "real_time_telemetry", "alert_on_anomalies"],
        "safety_boundaries": ["emergency_stop_required", "human_supervisor_required", "backup_systems_active"]
    }
    
    for section, required_keys in required_sections.items():
        if section not in sandbox_limits:
            raise ValueError(f"Missing required section '{section}' in sandbox_limits")
        
        section_data = sandbox_limits[section]
        if not isinstance(section_data, dict):
            raise ValueError(f"Section '{section}' must be a dictionary")
        
        for key in required_keys:
            if key not in section_data:
                raise ValueError(f"Missing required key '{key}' in sandbox_limits.{section}")
    
    # Validate specific safety values
    operating_area = sandbox_limits["operating_area"]
    if not isinstance(operating_area["max_radius_m"], (int, float)) or operating_area["max_radius_m"] <= 0:
        raise ValueError("operating_area.max_radius_m must be a positive number")
    
    if operating_area["require_geofence"] is not True:
        raise ValueError("operating_area.require_geofence must be True for safety")
    
    session_limits = sandbox_limits["session_limits"]
    if not isinstance(session_limits["max_duration_minutes"], int) or session_limits["max_duration_minutes"] <= 0:
        raise ValueError("session_limits.max_duration_minutes must be a positive integer")
    
    safety_boundaries = sandbox_limits["safety_boundaries"]
    critical_safety_keys = ["emergency_stop_required", "human_supervisor_required", "backup_systems_active"]
    for key in critical_safety_keys:
        if safety_boundaries[key] is not True:
            raise ValueError(f"safety_boundaries.{key} must be True for safety")


def load_policy():
    p = DEFAULT.copy()
    if os.path.exists(TOPIC_CONFIG_FILE):
        try:
            cfg = yaml.safe_load(open(TOPIC_CONFIG_FILE, "r", encoding="utf-8")) or {}
            rob = cfg.get("robotics", {})
            p.update(
                {
                    k: v
                    for k, v in rob.items()
                    if k in DEFAULT or k in {"focus", "sandbox_limits"}
                }
            )
            
            # Validate sandbox_limits if present
            if "sandbox_limits" in p:
                try:
                    validate_sandbox_limits(p["sandbox_limits"])
                except ValueError as e:
                    logging.error(f"Invalid sandbox_limits configuration: {e}")
                    # Remove invalid sandbox_limits to prevent unsafe operation
                    del p["sandbox_limits"]
                    
        except Exception as e:
            logging.warning(f"Failed to load configuration from {TOPIC_CONFIG_FILE}: {e}")
            # Continue with defaults
    if os.getenv("ROBOTICS_ENABLE", "0").lower() in {"1", "true", "yes"}:
        p["enabled"] = True
    if os.getenv("ROBOTICS_REPAIR_ENABLE", "0").lower() in {"1", "true", "yes"}:
        p["self_repair_enabled"] = True
    return p
