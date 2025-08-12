import os, yaml
TOPIC_CONFIG_FILE = os.getenv("TOPIC_CONFIG_FILE", "topics.yml")
DEFAULT = {
  "enabled": False, "self_repair_enabled": False, "approve_required": True,
  "banned_terms": ["weapon","explosive","lockpick","chemical dispersal"],
  "materials_whitelist": ["PLA","PETG","TPU","aluminum 6061"],
  "actuator_limits": {"max_torque_Nm": 2.0, "max_speed_mps": 0.5},
}
def load_policy():
    p = DEFAULT.copy()
    if os.path.exists(TOPIC_CONFIG_FILE):
        try:
            cfg = yaml.safe_load(open(TOPIC_CONFIG_FILE,"r",encoding="utf-8")) or {}
            rob = cfg.get("robotics", {}); p.update({k:v for k,v in rob.items() if k in DEFAULT or k in {"focus"}})
        except: pass
    if os.getenv("ROBOTICS_ENABLE","0").lower() in {"1","true","yes"}: p["enabled"]=True
    if os.getenv("ROBOTICS_REPAIR_ENABLE","0").lower() in {"1","true","yes"}: p["self_repair_enabled"]=True
    return p
