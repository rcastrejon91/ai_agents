# 🧠 LYRA Codex

## 1. Overview
Lyra is a **multi-agent AI system** powered by OpenAI + Tavily search.  
It routes user requests to the right domain-specific agent (finance, legal, retail, etc.) and returns context-aware responses.

---

## 2. System Map

**Core API entrypoint:**  
`/api/lyra` → Routes input to the right agent → Calls agent logic → Returns reply.

**Agent files (in `/agents/`):**
- `finance_agent.py` → Financial analysis, budgeting, investments
- `frontend_agent.py` → UI/UX, design guidance, frontend code help
- `healthcare_agent.py` → General healthcare info & resources
- `legal_agent.py` → Legal context & compliance info
- `pricing_agent.py` → Pricing models, quotes, rate calculations
- `real_estate_agent.py` → Housing, property search, market trends
- `retail_agent.py` → Product search, eCommerce, inventory ideas
- `scene_context.py` → Tracks conversation & situational context

**Tools:**
- `OPENAI_API_KEY` → LLM reasoning & text generation
- `TAVILY_API_KEY` → Real-time web search & citations

---

## 3. Environment Variables

Set these in **Vercel** (and GitHub Actions secrets if deploying via CI):

```env
OPENAI_API_KEY=sk-xxxx
TAVILY_API_KEY=tvly-xxxx
LYRA_FREE_DAILY_SEARCH_LIMIT=25   # example limit before upgrade prompt
USE_LLM_ROUTER=true               # toggle between keyword vs AI intent routing
```

---

## 4. API Contract

POST `/api/lyra`

**Request:**
```json
{
  "query": "Find me the latest mortgage rates",
  "userId": "abc123"
}
```

**Response:**
```json
{
  "agent": "real_estate_agent",
  "reply": "The current average 30-year fixed mortgage rate is 6.89%...",
  "sources": [
    {"title": "Mortgage News Daily", "url": "https://..."}
  ]
}
```

**Error example (limit hit):**
```json
{
  "error": "dailyLimitReached",
  "message": "You've reached your free daily search limit. Upgrade to continue."
}
```

---

## 5. Routing Rules

**Default:** Keyword map → agent  
Example:

```python
if "mortgage" in query or "house" in query:
    agent = real_estate_agent
```

**Advanced (if `USE_LLM_ROUTER=true`):**  
Lyra asks OpenAI to pick the correct agent based on context.

---

## 6. Guardrails
- No unsafe or illegal instructions executed
- Medical/legal content returns disclaimer
- Sensitive searches → requires user confirmation
- All actions logged for internal review in case of investigation

---

## 7. Observability
- Logs: View Vercel → Function Logs
- Debug mode: `DEBUG=true` in env to print router decisions
- Optional: Connect Supabase/Postgres to log queries & responses

---

## 8. Rate Limits & Monetization
- Free tier: `LYRA_FREE_DAILY_SEARCH_LIMIT` searches/day
- On limit: return `dailyLimitReached` error + prompt user to upgrade
- Paid status: Check user’s plan flag from DB or Stripe API

---

## 9. Dev & Deploy

**Local Dev:**
```bash
git clone <repo>
cd lyra
pip install -r requirements.txt
cp .env.example .env.local
# Fill in your keys
npm run dev   # if frontend present
```

**Deploy:**
1. Push to main branch  
2. GitHub Actions triggers build  
3. Deploys to Vercel

---

## 10. Adding a New Agent
1. Create new file in `/agents/` (e.g. `travel_agent.py`)
2. Export a `handle(query, context)` function
3. Add to router in `/api/lyra`
4. Update docs here
5. Deploy

---

## 11. Changelog

**2025-08-11**
- Added Tavily real-time search integration
- Added daily limit + upgrade prompt
- Multi-agent routing enabled

---

## 12. Roadmap
- Self-renaming based on user tendencies
- Auto-improvement loop (learning from feedback)
- Multi-modal input (voice + image)
- Memory persistence across sessions

---
