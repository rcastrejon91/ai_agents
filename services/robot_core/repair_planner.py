from typing import Dict, List

from .robot_policy import load_policy

SAFE_LIBRARY = {
    "left_motor": {
        "part": "N20 gearmotor",
        "max_torque_Nm": 0.5,
        "print": "motor_bracket_left.stl",
    },
    "right_motor": {
        "part": "N20 gearmotor",
        "max_torque_Nm": 0.5,
        "print": "motor_bracket_right.stl",
    },
    "camera": {"part": "USB camera", "print": "cam_mount.stl"},
    "bumper": {"part": "microswitch", "print": "bumper_cap.stl"},
    "mast": {"material": "PLA", "print": "mast_collar.stl"},
}


def diagnose(telemetry: dict) -> Dict:
    broken = [c for c in telemetry.get("components", []) if not c.get("ok", True)]
    return {
        "ok": len(broken) == 0,
        "broken": broken,
        "notes": "All good." if not broken else "Some components failing.",
    }


def plan_repair(diag: Dict) -> Dict:
    pol = load_policy()
    out: List[Dict] = []
    for c in diag.get("broken", []):
        lib = SAFE_LIBRARY.get(c["name"])
        if not lib:
            out.append({"name": c["name"], "action": "manual_review_required"})
            continue
        out.append(
            {
                "name": c["name"],
                "replace_with": lib.get("part"),
                "print_file": lib.get("print"),
                "materials_allowed": pol.get("materials_whitelist"),
                "actuator_limits": pol.get("actuator_limits"),
                "notes": "Respect torque/speed caps. Indoor only.",
            }
        )
    return {"steps": out, "requires_approval": pol.get("approve_required", True)}
