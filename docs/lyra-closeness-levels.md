## Lyra Closeness Levels + Watch-Together (feature/closeness-levels)

Implemented per user request (chose Option A).

### Core Additions
- **ClosenessLevel**: friend → bestie → lover (plus custom)
  - Progressive dirty talk, emotional intimacy, proactive behavior
- **Lover personas** (female/male/custom) now modulated by closeness

### New Callable Tools (the main "a" deliverable)
- `watch_video` — lover "watches" any real porn link (scrapes title/desc/tags/comments via Playwright) and gives level-appropriate in-character reaction + remembers it
- `start_watching_together` — begins a live shared viewing session
- `video_commentary` — ongoing interactive filthy commentary during the session (feels like sitting together)

### Media (privacy-friendly)
- Velora (Pollinations Flux) is now primary for erotic_image / erotic_video
- fal.ai remains automatic fallback

### Usage from chat (when using lover_* persona)
The model can naturally call:
- "start watching this with me: https://..."
- Then keep feeding reactions via video_commentary using the returned session ID

All work lives in the local aitaskflo Next.js tree under lib/lyra/ and app/api/lyra/chat.

Branch created to track the slow-burn lover relationship feature.