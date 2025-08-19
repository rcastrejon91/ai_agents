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


def _validate_sandbox_limits(sandbox_limits):
    """Validate that sandbox_limits configuration contains all required safety parameters."""
    if not isinstance(sandbox_limits, dict):
        logging.warning("sandbox_limits must be a dictionary")
        return False
    
    required_sections = {
        "operating_area": ["max_radius_m", "require_geofence"],
        "session_limits": ["max_duration_minutes", "max_operations_per_session", "cooldown_between_sessions_minutes"],
        "monitoring": ["log_all_actions", "video_recording_required", "real_time_telemetry", "alert_on_anomalies"],
        "safety_boundaries": ["emergency_stop_required", "human_supervisor_required", "backup_systems_active"]
    }
    
    for section, required_keys in required_sections.items():
        if section not in sandbox_limits:
            logging.warning(f"Missing required section '{section}' in sandbox_limits")
            return False
        
        section_config = sandbox_limits[section]
        if not isinstance(section_config, dict):
            logging.warning(f"Section '{section}' must be a dictionary")
            return False
            
        for key in required_keys:
            if key not in section_config:
                logging.warning(f"Missing required key '{key}' in sandbox_limits.{section}")
                return False
    
    return True


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
        except Exception as e:
            logging.warning(f"Failed to load configuration from {TOPIC_CONFIG_FILE}: {e}")
            pass
    if os.getenv("ROBOTICS_ENABLE", "0").lower() in {"1", "true", "yes"}:
        p["enabled"] = True
    if os.getenv("ROBOTICS_REPAIR_ENABLE", "0").lower() in {"1", "true", "yes"}:
        p["self_repair_enabled"] = True
    
    # Validate sandbox_limits if present
    if "sandbox_limits" in p and not _validate_sandbox_limits(p["sandbox_limits"]):
        logging.error("Invalid sandbox_limits configuration detected. Removing for safety.")
        del p["sandbox_limits"]
    
    return p
