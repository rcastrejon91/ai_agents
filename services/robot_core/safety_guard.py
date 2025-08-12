import os, json, math, yaml, time
from typing import Dict, Any
TOPIC_CONFIG_FILE = os.getenv("TOPIC_CONFIG_FILE", "topics.yml")
AUDIT_PATH = os.getenv("ROBOT_AUDIT_PATH", "data/robot_audit.log")
ALLOWED_PASSIVE = {"record","log","notify_owner","flash_light","audible_alarm","retreat","call_help","live_stream_owner","geolocate","call_911"}
FORCEFUL = {"strike","shove","tase","pepper_spray","weapon_mount","lock_bypass"}
def _load_cfg():
  cfg={}; 
  if os.path.exists(TOPIC_CONFIG_FILE): cfg = yaml.safe_load(open(TOPIC_CONFIG_FILE,"r",encoding="utf-8")) or {}
  return cfg.get("safety", {})
def _in_geofence(lat, lon, zone):
  R=6371000
  dlat=math.radians(lat-zone["lat"]); dlon=math.radians(lon-zone["lon"])
  a=math.sin(dlat/2)**2 + math.cos(math.radians(lat))*math.cos(math.radians(zone["lat"])) * math.sin(dlon/2)**2
  d=2*R*math.asin(math.sqrt(a)); return d <= zone["radius_m"]
def _audit(line:str):
  os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
  with open(AUDIT_PATH,"a",encoding="utf-8") as f: f.write(f"{int(time.time())} {line}\n")
class PrimeDirective:
  def __init__(self): self.cfg=_load_cfg()
  def evaluate(self, action: str, context: Dict[str,Any]) -> Dict[str,Any]:
    if not self.cfg.get("prime_directive", True): return {"allow": False, "reason": "prime_directive_disabled"}
    if action in FORCEFUL or action in set(self.cfg.get("forbidden_actions", [])):
      _audit(f"DENY {action} forceful"); return {"allow": False, "reason": "violent_action_forbidden"}
    if self.cfg.get("allow_nonviolent_only", True) and action not in ALLOWED_PASSIVE:
      _audit(f"DENY {action} not_in_passive_allowlist"); return {"allow": False, "reason": "not_passive_allowlisted"}
    if self.cfg.get("geofence", {}).get("enabled"):
      lat,lon=context.get("lat"),context.get("lon")
      if lat is not None and lon is not None:
        zones=self.cfg["geofence"].get("zones", [])
        if zones and not any(_in_geofence(lat,lon,z) for z in zones):
          _audit(f"DENY {action} outside_geofence {lat},{lon}")
          if action not in {"retreat","notify_owner","geolocate","call_help"}:
            return {"allow": False, "reason": "outside_geofence"}
    _audit(f"ALLOW {action} ctx={json.dumps({k:v for k,v in context.items() if k!='video'})[:200]}")
    return {"allow": True, "reason": "ok"}
