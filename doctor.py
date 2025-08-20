import importlib
import os
import platform
import sys
import traceback


def ok(label):
    print(f"✅ {label}")


def bad(label, e=""):
    print(f"❌ {label}\n{e}")


print("=== Lyra System Doctor ===")
print("Python:", sys.version)
print("Platform:", platform.platform())

# 1) modules
for mod in ["flask", "flask_cors", "gpt4all"]:
    try:
        importlib.import_module(mod.replace("flask_cors", "flask_cors"))
        ok(f"import {mod}")
    except Exception:
        bad(f"import {mod}", traceback.format_exc())

# 2) package init files
paths = ["agents", "lyra_core", "robot_core"]
for p in paths:
    ip = os.path.join(p, "__init__.py")
    if os.path.isdir(p) and not os.path.exists(ip):
        bad(f"missing {ip}")
    else:
        ok(f"{p}/__init__.py exists")

# 3) model availability
model = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
models_dir = os.path.expanduser("~/.cache/gpt4all")
candidate = os.path.join(models_dir, model)
if os.path.exists(candidate):
    ok(f"model found: {candidate}")
else:
    print(f"ℹ️ model not found at {candidate} (will attempt download on first run)")

# 4) import orchestrator
try:
    ok("import lyra_core.lyra_ai:LyraAI")
except Exception:
    bad("import lyra_core.lyra_ai", traceback.format_exc())

print("=== Done ===")
