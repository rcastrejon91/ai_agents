# Entry: Frontend Stack Overview

**Scope:** `frontend_agent.py`, `dream_world_sim.py`, `guardian_protocols.py`, `guardian_phase_two.py`, `bots/core/launch_manager.py`

**Summary:** The frontend agent now adds two subsystems—`DreamWorldSim` (background imagination) and `GuardianProtocols` (basic safety pulse)—to its async pipeline. Results include `emotion`, `logic`, `dream`, `guardian`, and the generated `response`, all logged to memory. A playful Phase II package introduces archetype agents, a quantum firewall + lockdown phrase, and a simple `CodexLore` engine for milestone notes. `LaunchManager` schedules background jobs and returns real APScheduler `Job` handles; tests verify execution.

**Why it matters:** Clear separation of concerns, safer responses, richer context, and observable scheduling.

**Next:** Replace keyword safety with a proper moderation layer; enrich dream simulation; admin UI for scheduled jobs.


⸻
