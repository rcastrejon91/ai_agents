"""
tool_creator.py — Lyra writes her own tools.
Creates Python tools on demand, saves to tools/, registers in tools/registry.json.
"""

import os, json, importlib.util, subprocess
from pathlib import Path

TOOLS_DIR = Path(__file__).parent / "tools"
REGISTRY_FILE = TOOLS_DIR / "registry.json"

_WRITER_PROMPT = """You are a Python tool writer for Lyra.

Respond in EXACTLY this format (no extra text):

NAME: snake_case_name
DESC: one sentence description
PARAMS: {"param": "type - description"}
CODE:
def snake_case_name(**kwargs):
    try:
        # implementation here
        return {"result": "value"}
    except Exception as e:
        return {"error": str(e)}

Rules:
- Function name matches NAME exactly
- ALL imports inside the function body
- Return a dict with at least a "result" key
- Only use stdlib or: requests, json, os, datetime
- Under 40 lines"""


def _load_registry() -> dict:
    if not REGISTRY_FILE.exists():
        return {}
    with open(REGISTRY_FILE) as f:
        return json.load(f)


def _save_registry(registry: dict):
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)


def create_tool(description: str) -> dict:
    """Ask Groq to write a new tool, save it, and register it."""
    api_key = os.environ.get("GROQ_API_KEY", "")
    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 2000,
        "messages": [
            {"role": "system", "content": _WRITER_PROMPT},
            {"role": "user", "content": "Create a tool that: " + description}
        ]
    })
    result = subprocess.run([
        "curl", "-s", "https://api.groq.com/openai/v1/chat/completions",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "content-type: application/json",
        "-d", payload
    ], capture_output=True, text=True, timeout=60)
    data = json.loads(result.stdout)
    if "error" in data:
        raise Exception(data["error"])
    raw = data["choices"][0]["message"]["content"].strip()

    # Parse delimiter format
    lines = raw.split("\n")
    name, desc, params_str, code_lines = "", "", "{}", []
    in_code = False
    for line in lines:
        if line.startswith("NAME:"):
            name = line[5:].strip()
        elif line.startswith("DESC:"):
            desc = line[5:].strip()
        elif line.startswith("PARAMS:"):
            params_str = line[7:].strip()
        elif line.startswith("CODE:"):
            in_code = True
        elif in_code:
            # strip markdown fences
            if line.strip().startswith("```"):
                continue
            code_lines.append(line)

    if not name:
        raise Exception(f"Could not parse tool response: {raw[:200]}")

    try:
        params = json.loads(params_str)
    except Exception:
        params = {}

    meta = {
        "name": name,
        "description": desc,
        "parameters": params,
        "code": "\n".join(code_lines).strip(),
    }
    name = meta["name"]

    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    tool_file = TOOLS_DIR / (name + ".py")
    with open(tool_file, "w") as f:
        f.write(meta["code"])

    registry = _load_registry()
    registry[name] = {
        "name": name,
        "description": meta["description"],
        "parameters": meta.get("parameters", {}),
        "file": str(tool_file),
        "function": name,
    }
    _save_registry(registry)

    return {
        "name": name,
        "description": meta["description"],
        "parameters": meta.get("parameters", {}),
        "file": str(tool_file),
    }


def run_tool(name: str, params: dict = None) -> dict:
    """Load a registered tool by name and call it with params."""
    registry = _load_registry()
    if name not in registry:
        available = list(registry.keys())
        return {"error": f"Tool '{name}' not found. Available: {available}"}

    info = registry[name]
    raw_path = Path(info["file"])
    # Support both absolute paths and relative paths stored in registry
    tool_file = raw_path if raw_path.is_absolute() else TOOLS_DIR.parent / raw_path
    if not tool_file.exists():
        return {"error": f"Tool file missing: {tool_file}"}

    spec = importlib.util.spec_from_file_location(name, tool_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    func = getattr(module, info["function"])
    return func(**(params or {}))


def list_tools() -> list:
    """Return all registered tools as a list of dicts."""
    registry = _load_registry()
    return [
        {
            "name": k,
            "description": v["description"],
            "parameters": v.get("parameters", {}),
        }
        for k, v in registry.items()
    ]
