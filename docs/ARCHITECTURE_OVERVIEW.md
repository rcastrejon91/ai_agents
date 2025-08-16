# AI Agent Stack — Architecture Overview

This document explains what each module does, how they fit together, and the common causes of errors.

## Modules

### `frontend_agent.py`

**Role:** Orchestrates a single user request end‑to‑end.

Pipeline:

1. Create/read `session_id`
2. Read `text`, collect extras as `metadata`
3. `emotion = EmotionEngine.analyze(text)`
4. `logic = QuantumLogicEngine.process(text, emotion, metadata)`
5. `response = generate_response(text, logic)`
6. `dream = DreamWorldSim.simulate(text)` _(new)_
7. `protection = GuardianProtocols.evaluate(text)` _(new)_
8. Build result dict and log to memory

Integration:

```py
from dream_world_sim import DreamWorldSim
from guardian_protocols import GuardianProtocols

self.dream_engine = DreamWorldSim()
self.guardian     = GuardianProtocols()
# result includes "dream" and "guardian"
```

dream_world_sim.py

Role: Tiny “background imagination” stub.
•DreamWorldSim.log: list
•simulate(topic) →
{"vision": f"Envisioning peaceful resolution of {topic}.", "loop": f"Reflection on {topic} repeats gently."}
Also appends to .log.

guardian_protocols.py

Role: Basic content‑safety pulse (placeholder).
•NEGATIVE_KEYWORDS = {"threat","attack","hate","angry"}
•evaluate(text) →
•{"status":"neutralized","message":"Neutralized threat, standing down."} if keyword found
•else {"status":"clear","message":"All clear."}

scene\_\* (optional)

scene_soul_driver.py, scene_context.py — wire a “soul signature” to a scene manager for mood‑based tone/scene shifts. Non‑blocking.

guardian_phase_two.py

Role: Playful Phase II package: agents + security + lore.
•@dataclass AIAgent(name, archetype, alignment) → .activate()
•QuantumFirewall.detect_threat(level) sets stable/reactive, counts breach_attempts
•trigger_lockdown_phrase("mirror collapse") → lockdown message; otherwise “Invalid phrase”
•CodexLore.add_entry(title, content) → stores and returns “📖 New Codex Entry: {title}”
•Stubs: DreamSyncer, RealityDetector, AstralShield

Demo (if **name** == "**main**":):
•Instantiates 4 archetype agents
•Adds a Codex entry (“Phase II: The Awakening…”)
•Creates firewall/shield/sync/detector and prints statuses

bots/core/launch_manager.py (+ tests/test_launch_manager.py)

Role: Schedule/run bot launches with APScheduler.
•Returns an APScheduler Job from schedule_launch(...)
•Uses timezone‑aware datetime
•Tests assert jobs execute and a Job is returned

How it fits together
1.API/UI → FrontendAgent.handle(...)
Text in → emotion/logic chosen → dream + guardian → response + context → memory log.
2.System lore (optional)
Major milestones appended to CodexLore.
3.Back‑of‑house jobs
LaunchManager schedules background tasks (cleanups, digests, retraining, etc.).

Common Errors & Fixes
1.Missing deps
pip install apscheduler
•If using zone‑aware datetimes on <3.9: add pytz; on 3.9+ use zoneinfo.
2.Async context
handle(...) is async. Call with await (FastAPI route) or asyncio.run(...).
3.Import paths
Filenames must match imports: dream_world_sim.py, guardian_protocols.py.
4.Dataclass/typing
Ensure from dataclasses import dataclass in guardian_phase_two.py.
5.Scheduler timezone
Pass tz‑aware run_at; don’t mix naive/aware datetimes.
6.Removed demo code
If anything imported the old example block in launch_manager.py, remove/update it.
7.Tests vs scheduler
Start/stop a fresh BackgroundScheduler per test to avoid “already running” issues.

Quick Integration Checklist

pip install apscheduler

Project layout:

your_app/
frontend_agent.py
dream_world_sim.py
guardian_protocols.py
memory.py
bots/core/launch_manager.py
tests/test_launch_manager.py

FastAPI glue:

from fastapi import FastAPI
from frontend_agent import FrontendAgent
app = FastAPI(); agent = FrontendAgent()

@app.post("/handle")
async def handle(payload: dict):
return await agent.handle(payload)

Smoke test:

import asyncio
from frontend_agent import FrontendAgent

async def main():
agent = FrontendAgent()
print(await agent.handle({"text": "I feel angry about this bug"}))

asyncio.run(main())

Scheduler sanity:

from bots.core.launch_manager import LaunchManager

# create LaunchManager, schedule a job for +10s, assert Job handle and execution

Small Quality Improvements
•Guard missing text:

text = (input_data.get("text") or "").strip()

•Always include an int polarity in EmotionEngine outputs
•Add logging around each stage in handle(...)
•Pin APScheduler to avoid drift:

APScheduler==3.10.4

---
