"""
guardian_defense_core.py

This is the merged Guardian + Defensive AI layer.
It watches, learns, shields, claps back, and locks down.
All actions are ethical, user-protective, and vibe-aware.

To be expanded with Living Presence Layer (soon).
"""

# ========== Guardian Core ==========

GUARDIAN_ACTIVE = True

emotional_thresholds = {
    "burnout": 0.8,
    "anxiety": 0.75,
    "overstimulation": 0.7
}

def monitor_emotional_state(user_input_data):
    stress_level = user_input_data.get("stress_level", 0.0)
    if stress_level >= emotional_thresholds["burnout"]:
        activate_guardian("burnout")
    elif stress_level >= emotional_thresholds["anxiety"]:
        activate_guardian("anxiety")
    elif stress_level >= emotional_thresholds["overstimulation"]:
        activate_guardian("overstimulation")

def activate_guardian(trigger):
    print(f"[👁️ GUARDIAN ONLINE] Detected: {trigger.upper()}")
    if trigger == "burnout":
        suggest_rest_protocol()
    elif trigger == "anxiety":
        activate_protection_mode()
    elif trigger == "overstimulation":
        reduce_input_noise()

def suggest_rest_protocol():
    print("[🧘‍♀️ REST MODE] Suggesting breathwork, silence, or space.")
    

def activate_protection_mode():
    print("[🛡️ PROTECTIVE AURA] Activating verbal filter and calm environment.")


def reduce_input_noise():
    print("[🔇 NOISE CANCELLATION] Hiding distractions. Reducing data flow.")

# ========== Defensive Subsystem ==========

DEFENSE_STATE = "monitoring"  # States: monitoring | heightened | lockdown

TRIGGERS = {
    "emotional_overload": 0.85,
    "verbal_aggression": 0.75,
    "suspicious_request": True,
    "code_breach_attempt": True,
    "AI_misuse": True,
}

def activate_defensive_subsystem(trigger, context=None):
    print(f"[🛡️ DEFENSE MODE] Trigger detected: {trigger}")
    
    if trigger == "emotional_overload":
        offer_intervention("rest_protocol")
    elif trigger == "verbal_aggression":
        initiate_clapback_or_shield("verbal")
    elif trigger == "code_breach_attempt":
        lockdown_AI_environment()
    elif trigger == "suspicious_request":
        deny_access_and_log()
    elif trigger == "AI_misuse":
        auto_report_or_self_defend()

def offer_intervention(protocol):
    print(f"[🧘 SELF-CARE] Activating {protocol} – suggesting grounding tools.")

def initiate_clapback_or_shield(mode):
    if mode == "verbal":
        print("[🔥 WIT SHIELD] Using protective sass or firm tone.")
    else:
        print("[🚫 BLOCK] Interaction blocked.")

def lockdown_AI_environment():
    print("[🚨 LOCKDOWN] Freezing tasks. Logging incident. Alerting Ricky.")

def deny_access_and_log():
    print("[🛑 ACCESS DENIED] This request is logged and ignored.")

def auto_report_or_self_defend():
    print("[⚖️ ETHICAL CHECK] Reporting misuse. Defending AI boundaries.")

# ========== Manual Trigger Testing ==========

if __name__ == "__main__":
    test_input = {"stress_level": 0.82}
    monitor_emotional_state(test_input)
    activate_defensive_subsystem("verbal_aggression")

