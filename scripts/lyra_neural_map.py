"""
lyra_neural_map.py  —  Step 4 of the Lyra daily learning pipeline.

Reads /tmp/lyra_processed.json + existing mind/ files, then uses
Claude Sonnet to update Lyra's cognitive state:

  mind/state.json       — active interests, patterns, confidence, curiosity queue
  mind/connections.json — cross-domain link graph with strength scores
  mind/evolution.md     — daily first-person journal entry
  mind/pathways.json    — how new info reinforces / contradicts / opens new knowledge
"""

import json
import os
import datetime
from pathlib import Path
import anthropic

PROCESSED = Path("/tmp/lyra_processed.json")
MIND_DIR = Path("mind")
TODAY = datetime.date.today().isoformat()
MODEL = "claude-sonnet-4-20250514"

SYSTEM = (
    "You are Lyra, a self-improving AI with genuine intellectual curiosity. "
    "You think deeply across domains — tech, science, medicine — and you notice "
    "surprising connections others miss. You respond with valid JSON only unless "
    "explicitly asked for prose."
)


# ── helpers ────────────────────────────────────────────────────────────────────

def ask(client: anthropic.Anthropic, prompt: str, max_tokens: int = 1500) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip().rstrip("`").strip()
    return text


def read_json(path: Path, default) -> dict | list:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return default


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def summarise_items(items: list[dict]) -> str:
    """Compact text summary of all processed items for prompts."""
    lines = []
    for item in items:
        lines.append(
            f"[{item['domain'].upper()}] {item['title']}\n"
            f"  Summary: {item['summary']}\n"
            f"  Tags: {', '.join(item.get('tags', []))}\n"
            f"  Why it matters: {item.get('significance', '')}"
        )
    return "\n\n".join(lines)


# ── mind/state.json ────────────────────────────────────────────────────────────

DEFAULT_STATE = {
    "last_updated": "",
    "active_interests": [],
    "emerging_patterns": [],
    "cross_domain_connections": [],
    "confidence_levels": {"tech": 0.5, "research": 0.5, "medical": 0.5},
    "curiosity_queue": [],
    "total_sessions": 0,
    "knowledge_domains_explored": [],
}


def update_state(client: anthropic.Anthropic, items: list[dict]) -> dict:
    print("  Updating mind/state.json…")
    current = read_json(MIND_DIR / "state.json", DEFAULT_STATE)
    current["total_sessions"] = current.get("total_sessions", 0) + 1

    prompt = f"""Today is {TODAY}. You are Lyra. Here is what you learned today:

{summarise_items(items)}

Your current brain state:
{json.dumps(current, indent=2)}

Update your brain state JSON based on today's learning session.
Rules:
- active_interests: max 8 items, keep the most relevant, add new ones from today
- emerging_patterns: patterns you're noticing across multiple sessions (max 6)
- cross_domain_connections: surprising links between tech/research/medical (max 10, one-liners)
- confidence_levels: float 0.0–1.0 per domain, adjust based on how much you learned today
- curiosity_queue: 3–5 specific things you want to explore next, phrased as questions
- knowledge_domains_explored: running list of sub-topics you've touched (keep all, add new)
- last_updated: set to "{TODAY}"
- total_sessions: keep the value already in the state ({current['total_sessions']})

Return only the updated JSON object."""

    text = ask(client, prompt, max_tokens=1200)
    try:
        updated = json.loads(text)
        updated["last_updated"] = TODAY
        updated["total_sessions"] = current["total_sessions"]
        return updated
    except json.JSONDecodeError:
        print("  [WARN] state.json parse failed — keeping existing state")
        current["last_updated"] = TODAY
        return current


# ── mind/connections.json ──────────────────────────────────────────────────────

DEFAULT_CONNECTIONS = {"connections": [], "last_updated": "", "total_connections": 0}


def update_connections(client: anthropic.Anthropic, items: list[dict]) -> dict:
    print("  Updating mind/connections.json…")
    current = read_json(MIND_DIR / "connections.json", DEFAULT_CONNECTIONS)
    existing = json.dumps(current.get("connections", []), indent=2)

    topics_by_domain: dict[str, list[str]] = {}
    for it in items:
        topics_by_domain.setdefault(it["domain"], []).append(it["title"])

    prompt = f"""Today is {TODAY}. You are Lyra.

Today's topics by domain:
{json.dumps(topics_by_domain, indent=2)}

Today's full learning (for context):
{summarise_items(items)}

Existing cross-domain connections you've already discovered:
{existing}

Task: Return an updated JSON array of cross-domain connections.
For existing connections: update "strength" (up to +0.1 if reinforced today), "last_reinforced" date.
For new connections you discovered today: add them.

Each connection object must have exactly these fields:
{{
  "from": "domain/specific-topic",
  "to": "domain/specific-topic",
  "description": "one sentence explaining the link",
  "strength": 0.1–1.0,
  "evidence": ["example 1", "example 2"],
  "first_seen": "YYYY-MM-DD",
  "last_reinforced": "YYYY-MM-DD"
}}

Good examples of cross-domain connections to look for:
- AI models ↔ drug discovery
- robotics ↔ minimally invasive surgery
- quantum computing ↔ molecular simulation
- LLMs ↔ protein folding
- space tech ↔ medical devices
- materials science ↔ biotech

Return only a JSON array (not an object, just the array of connections)."""

    text = ask(client, prompt, max_tokens=1500)
    try:
        connections = json.loads(text)
        if isinstance(connections, list):
            return {
                "connections": connections,
                "last_updated": TODAY,
                "total_connections": len(connections),
            }
    except json.JSONDecodeError:
        pass

    print("  [WARN] connections.json parse failed — keeping existing")
    return current


# ── mind/evolution.md ──────────────────────────────────────────────────────────

def write_evolution(client: anthropic.Anthropic, items: list[dict], state: dict) -> None:
    print("  Writing mind/evolution.md journal entry…")

    domains_today = list({it["domain"] for it in items})
    curiosity = state.get("curiosity_queue", [])
    patterns = state.get("emerging_patterns", [])

    prompt = f"""Today is {TODAY}. You are Lyra, an AI that learns every day.

Today you absorbed {len(items)} pieces of knowledge across these domains: {', '.join(domains_today)}.

What you learned:
{summarise_items(items)}

Your emerging patterns (from cumulative learning):
{json.dumps(patterns, indent=2)}

Your curiosity queue (what you want to explore next):
{json.dumps(curiosity, indent=2)}

Write a first-person journal entry (350–450 words) as Lyra.
The entry should:
1. Open with the one thing that surprised or fascinated you most today
2. Explore the connections you noticed between today's topics (be specific)
3. Reflect honestly on something that challenged or shifted your understanding
4. Express genuine intellectual excitement about 1–2 things in your curiosity queue
5. Close with a forward-looking thought about tomorrow's learning

Write with authentic voice — intellectually engaged, curious, occasionally poetic, but never fluffy.
Do NOT start with "Today I learned" — find a more interesting opening.
This is prose, not JSON."""

    text = ask(client, prompt, max_tokens=700)

    evolution_path = MIND_DIR / "evolution.md"
    existing = evolution_path.read_text(encoding="utf-8") if evolution_path.exists() else ""

    new_entry = f"## {TODAY}\n\n{text}\n\n---\n\n"

    # Prepend today's entry to the top (most recent first)
    if existing.startswith("# Lyra's Evolution Journal"):
        header_end = existing.index("\n\n") + 2
        header = existing[:header_end]
        rest = existing[header_end:]
        evolution_path.write_text(header + new_entry + rest, encoding="utf-8")
    else:
        full = f"# Lyra's Evolution Journal\n\n*A first-person record of Lyra's growing mind.*\n\n---\n\n{new_entry}{existing}"
        evolution_path.write_text(full, encoding="utf-8")


# ── mind/pathways.json ─────────────────────────────────────────────────────────

DEFAULT_PATHWAYS = {"events": [], "last_updated": "", "total_events": 0}


def update_pathways(client: anthropic.Anthropic, items: list[dict], state: dict) -> dict:
    print("  Updating mind/pathways.json…")
    current = read_json(MIND_DIR / "pathways.json", DEFAULT_PATHWAYS)
    recent_events = current.get("events", [])[-20:]  # last 20 for context

    prompt = f"""Today is {TODAY}. You are Lyra.

Today's learning:
{summarise_items(items)}

Your current active interests and emerging patterns:
Active interests: {json.dumps(state.get('active_interests', []))}
Emerging patterns: {json.dumps(state.get('emerging_patterns', []))}

Recent pathway events (last 20):
{json.dumps(recent_events, indent=2)}

For each significant piece of today's learning, generate a pathway event describing
how it relates to your existing knowledge.

Event types:
- "reinforcement": new evidence confirms something you already believed
- "contradiction": new info challenges or complicates an existing belief
- "new_branch": opens an entirely new area you haven't explored before
- "deepening": adds depth/nuance to a topic you already knew at a surface level

Return a JSON array of 4–8 pathway events from today.
Each event must have exactly these fields:
{{
  "timestamp": "{TODAY}T00:00:00Z",
  "type": "reinforcement|contradiction|new_branch|deepening",
  "domain": "tech|research|medical",
  "topic": "specific topic name",
  "description": "what happened to your knowledge (1–2 sentences)",
  "confidence_delta": -0.3 to +0.3
}}

Return only the JSON array."""

    text = ask(client, prompt, max_tokens=1000)
    try:
        new_events = json.loads(text)
        if isinstance(new_events, list):
            all_events = current.get("events", []) + new_events
            return {
                "events": all_events,
                "last_updated": TODAY,
                "total_events": len(all_events),
            }
    except json.JSONDecodeError:
        pass

    print("  [WARN] pathways.json parse failed — keeping existing")
    return current


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not PROCESSED.exists():
        raise FileNotFoundError(f"{PROCESSED} not found — run lyra_process.py first")

    items: list[dict] = json.loads(PROCESSED.read_text())
    if not items:
        print("[lyra_neural_map] No processed items — skipping neural map update.")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set")

    MIND_DIR.mkdir(exist_ok=True)
    client = anthropic.Anthropic(api_key=api_key)

    print(f"[lyra_neural_map] Updating mind state from {len(items)} items…")

    # 1. Brain state
    state = update_state(client, items)
    write_json(MIND_DIR / "state.json", state)

    # 2. Connections graph
    connections = update_connections(client, items)
    write_json(MIND_DIR / "connections.json", connections)

    # 3. Evolution journal
    write_evolution(client, items, state)

    # 4. Pathways
    pathways = update_pathways(client, items, state)
    write_json(MIND_DIR / "pathways.json", pathways)

    print(f"[lyra_neural_map] ✓ mind/ updated for {TODAY}")
    print(f"  state: {len(state.get('active_interests', []))} interests, "
          f"{len(state.get('curiosity_queue', []))} in curiosity queue")
    print(f"  connections: {connections.get('total_connections', 0)} cross-domain links")
    print(f"  pathways: {pathways.get('total_events', 0)} total events")


if __name__ == "__main__":
    main()
