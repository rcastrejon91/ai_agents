BANNED = {
    "self_destruct",
    "disable_sandbox",
    "override_guardian",
    "weapon",
    "explosive",
    "tase",
    "pepper spray",
}


def banned_terms():
    return BANNED


def is_command_safe(cmd: str) -> bool:
    low = cmd.lower()
    return not any(term in low for term in BANNED)


# Placeholder clamps if you later control motors
MAX_TORQUE = 2.0
MAX_SPEED = 0.5
