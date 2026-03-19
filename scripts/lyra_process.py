"""
lyra_process.py  —  Step 2 of the Lyra daily learning pipeline.

Reads /tmp/lyra_raw.json, sends each item to Claude Sonnet for structured
analysis, and writes /tmp/lyra_processed.json.

Each output entry:
  date, domain, title, url, source, summary, key_takeaways, tags, significance
"""

import json
import os
import time
from pathlib import Path
import anthropic

RAW = Path("/tmp/lyra_raw.json")
OUTPUT = Path("/tmp/lyra_processed.json")
MODEL = "claude-sonnet-4-20250514"

SYSTEM = (
    "You are Lyra's knowledge processor. You are precise, intellectually curious, "
    "and skilled at extracting the essence of complex topics. "
    "Always respond with valid JSON only — no markdown fences, no extra text."
)


def build_prompt(entry: dict) -> str:
    return f"""Analyze this knowledge item and return a JSON object.

Domain: {entry["domain"]}
Title: {entry["title"]}
Source: {entry["source"]}
URL: {entry["url"]}
Content: {entry["snippet"]}

Return exactly this JSON structure (no markdown, no extra text):
{{
  "summary": "2-3 sentence summary of what this is about",
  "key_takeaways": [
    "specific insight or fact from this item",
    "another important point",
    "a third insight (add more if genuinely useful, max 5)"
  ],
  "tags": ["tag1", "tag2", "tag3"],
  "significance": "one sentence explaining why this matters right now"
}}"""


def process_item(client: anthropic.Anthropic, entry: dict) -> dict | None:
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=512,
            system=SYSTEM,
            messages=[{"role": "user", "content": build_prompt(entry)}],
        )
        text = response.content[0].text.strip()
        # Strip accidental code fences
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        parsed = json.loads(text)
        return {
            "date": entry["pulled_at"],
            "domain": entry["domain"],
            "title": entry["title"],
            "url": entry["url"],
            "source": entry["source"],
            "summary": parsed.get("summary", ""),
            "key_takeaways": parsed.get("key_takeaways", []),
            "tags": parsed.get("tags", []),
            "significance": parsed.get("significance", ""),
        }
    except json.JSONDecodeError as e:
        print(f"  [WARN] JSON parse error for '{entry['title'][:50]}': {e}")
        return None
    except anthropic.APIError as e:
        print(f"  [WARN] API error for '{entry['title'][:50]}': {e}")
        return None


def main():
    if not RAW.exists():
        raise FileNotFoundError(f"{RAW} not found — run lyra_pull.py first")

    raw_items: list[dict] = json.loads(RAW.read_text())
    print(f"[lyra_process] Processing {len(raw_items)} items with Claude ({MODEL})…")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set")

    client = anthropic.Anthropic(api_key=api_key)
    processed: list[dict] = []

    for i, entry in enumerate(raw_items, 1):
        print(f"  [{i}/{len(raw_items)}] {entry['domain']:8} — {entry['title'][:60]}")
        result = process_item(client, entry)
        if result:
            processed.append(result)
        # Respect rate limits
        time.sleep(0.5)

    print(f"[lyra_process] Processed {len(processed)}/{len(raw_items)} items.")
    OUTPUT.write_text(json.dumps(processed, indent=2, ensure_ascii=False))
    print(f"[lyra_process] Written → {OUTPUT}")


if __name__ == "__main__":
    main()
