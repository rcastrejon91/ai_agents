import logging
import os

import yaml

# Setup logging for robot policy
logger = logging.getLogger(__name__)

TOPIC_CONFIG_FILE = os.getenv("TOPIC_CONFIG_FILE", "topics.yml")
DEFAULT = {
    "enabled": False,
    "self_repair_enabled": False,
    "approve_required": True,
    "banned_terms": ["weapon", "explosive", "lockpick", "chemical dispersal"],
    "materials_whitelist": ["PLA", "PETG", "TPU", "aluminum 6061"],
    "actuator_limits": {"max_torque_Nm": 2.0, "max_speed_mps": 0.5},
}

# Required safety parameters that must be present when robotics is enabled
REQUIRED_SAFETY_PARAMS = [
    "approve_required",
    "banned_terms",
    "materials_whitelist",
    "actuator_limits",
]


def validate_policy_config(policy):
    """Validate that all required safety parameters are present and properly configured."""
    validation_errors = []

    # Check required safety parameters
    for param in REQUIRED_SAFETY_PARAMS:
        if param not in policy:
            validation_errors.append(f"Missing required safety parameter: {param}")
        elif not policy[param]:
            validation_errors.append(f"Safety parameter cannot be empty: {param}")

    # Validate actuator limits if present
    if "actuator_limits" in policy:
        limits = policy["actuator_limits"]
        if not isinstance(limits, dict):
            validation_errors.append("actuator_limits must be a dictionary")
        else:
            if "max_torque_Nm" not in limits or limits["max_torque_Nm"] <= 0:
                validation_errors.append("max_torque_Nm must be positive")
            if "max_speed_mps" not in limits or limits["max_speed_mps"] <= 0:
                validation_errors.append("max_speed_mps must be positive")

    # Validate banned terms
    if "banned_terms" in policy and not isinstance(policy["banned_terms"], list):
        validation_errors.append("banned_terms must be a list")

    # Validate materials whitelist
    if "materials_whitelist" in policy and not isinstance(
        policy["materials_whitelist"], list
    ):
        validation_errors.append("materials_whitelist must be a list")

    # Critical safety check: approve_required must always be True when enabled
    if policy.get("enabled", False) and not policy.get("approve_required", False):
        validation_errors.append(
            "approve_required must be True when robotics is enabled"
        )

    return validation_errors


def check_environment_safety():
    """Check for dangerous environment variable combinations."""
    warnings = []

    # Check if both robotics and self-repair are being enabled via env vars
    robotics_enabled = os.getenv("ROBOTICS_ENABLE", "0").lower() in {"1", "true", "yes"}
    repair_enabled = os.getenv("ROBOTICS_REPAIR_ENABLE", "0").lower() in {
        "1",
        "true",
        "yes",
    }

    if robotics_enabled and repair_enabled:
        warnings.append(
            "WARNING: Both ROBOTICS_ENABLE and ROBOTICS_REPAIR_ENABLE are set - this enables autonomous operation"
        )

    if repair_enabled and not robotics_enabled:
        warnings.append(
            "WARNING: ROBOTICS_REPAIR_ENABLE is set but ROBOTICS_ENABLE is not - self-repair requires robotics to be enabled"
        )

    return warnings


def load_policy():
    p = DEFAULT.copy()

    # Check for dangerous environment variable combinations first
    env_warnings = check_environment_safety()
    for warning in env_warnings:
        logger.warning(warning)

    if os.path.exists(TOPIC_CONFIG_FILE):
        try:
            cfg = yaml.safe_load(open(TOPIC_CONFIG_FILE, encoding="utf-8")) or {}
            rob = cfg.get("robotics", {})
            p.update(
                {
                    k: v
                    for k, v in rob.items()
                    if k in DEFAULT or k in {"focus", "sandbox_limits"}
                }
            )
        except Exception as e:
            logger.warning(
                f"Failed to load configuration from {TOPIC_CONFIG_FILE}: {str(e)}"
            )
            logger.info("Using default robotics policy configuration")

    # Apply environment variable overrides with safety checks
    if os.getenv("ROBOTICS_ENABLE", "0").lower() in {"1", "true", "yes"}:
        logger.info("Robotics enabled via ROBOTICS_ENABLE environment variable")
        p["enabled"] = True

    if os.getenv("ROBOTICS_REPAIR_ENABLE", "0").lower() in {"1", "true", "yes"}:
        # Only allow self-repair if robotics is also enabled
        if p.get("enabled", False):
            logger.warning(
                "Self-repair enabled via ROBOTICS_REPAIR_ENABLE environment variable - this enables autonomous operation"
            )
            p["self_repair_enabled"] = True
        else:
            logger.error(
                "ROBOTICS_REPAIR_ENABLE is set but robotics is not enabled - ignoring self-repair setting for safety"
            )

    # Validate the final policy configuration
    if p.get("enabled", False):
        validation_errors = validate_policy_config(p)
        if validation_errors:
            logger.error("Robotics policy validation failed:")
            for error in validation_errors:
                logger.error(f"  - {error}")
            logger.error("Disabling robotics due to configuration errors")
            p["enabled"] = False
            p["self_repair_enabled"] = False
        else:
            logger.info("Robotics policy validation passed")

    return p
