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
        except:
            pass
    if os.getenv("ROBOTICS_ENABLE", "0").lower() in {"1", "true", "yes"}:
        p["enabled"] = True
    if os.getenv("ROBOTICS_REPAIR_ENABLE", "0").lower() in {"1", "true", "yes"}:
        p["self_repair_enabled"] = True
    return p


def update_self_repair_setting(enabled: bool) -> bool:
    """
    Update the self_repair_enabled setting in the topics.yml file.
    
    Args:
        enabled: Whether to enable or disable self-repair
        
    Returns:
        True if update was successful, False otherwise
        
    Note:
        This function maintains all other safety settings and only modifies
        the self_repair_enabled flag. The approve_required setting remains
        unchanged to ensure human approval is always required.
    """
    try:
        # Load existing configuration or create new one
        cfg = {}
        if os.path.exists(TOPIC_CONFIG_FILE):
            with open(TOPIC_CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
        
        # Ensure robotics section exists
        if "robotics" not in cfg:
            cfg["robotics"] = {}
        
        # Update only the self_repair_enabled setting
        cfg["robotics"]["self_repair_enabled"] = enabled
        
        # Ensure critical safety settings are maintained
        if "approve_required" not in cfg["robotics"]:
            cfg["robotics"]["approve_required"] = True
        
        # Write back to file
        with open(TOPIC_CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f, default_flow_style=False, indent=2)
        
        return True
        
    except Exception as e:
        # Log error but don't expose details for security
        print(f"Error updating self-repair setting: {e}")
        return False
