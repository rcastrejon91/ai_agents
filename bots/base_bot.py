import json, os
from bots.llm_client import call_llm
from datetime import datetime
from pathlib import Path

INSTANCES_DIR = Path("/home/lyra/bots/instances")


def _search_web(query: str) -> str:
    """Web search via Tavily for learning unknown answers."""
    import requests
    key = os.environ.get("TAVILY_API_KEY", "")
    if not key:
        return ""
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": key, "query": query, "max_results": 3},
            timeout=8
        )
        results = resp.json().get("results", [])
        return "\n\n".join(r.get("title", "") + ": " + r.get("content", "") for r in results)[:2000]
    except Exception:
        return ""


def scrape_url(url: str) -> str:
    """Extract clean text content from a URL using Tavily extract."""
    from tavily import TavilyClient
    key = os.environ.get("TAVILY_API_KEY", "")
    if not key:
        raise ValueError("TAVILY_API_KEY not set")
    client = TavilyClient(key)
    response = client.extract(urls=[url])
    results = response.get("results", [])
    if not results:
        return ""
    # Combine all extracted content
    text = "\n\n".join(
        r.get("raw_content", "") or r.get("content", "")
        for r in results
    )
    return text[:10000]  # Cap at 10k chars per URL


def _load_knowledge(bot_id: str) -> dict:
    f = INSTANCES_DIR / bot_id / "knowledge.json"
    return json.load(open(f)) if f.exists() else {"uploaded": "", "learned": [], "sources": []}


def _save_knowledge(bot_id: str, knowledge: dict):
    with open(INSTANCES_DIR / bot_id / "knowledge.json", "w") as f:
        json.dump(knowledge, f, indent=2)


def _load_config(bot_id: str):
    f = INSTANCES_DIR / bot_id / "config.json"
    return json.load(open(f)) if f.exists() else None


def _knowledge_search(question: str, knowledge: dict) -> str:
    words = [w for w in question.lower().split() if len(w) > 3]
    for item in knowledge.get("learned", []):
        if item.get("answer") and any(w in item.get("question", "").lower() for w in words):
            return item["answer"]
    uploaded = knowledge.get("uploaded", "")
    if uploaded and any(w in uploaded.lower() for w in words):
        return uploaded
    return ""


def chat(bot_id: str, message: str, conversation_history: list = None) -> dict:
    config = _load_config(bot_id)
    if not config:
        return {"reply": "Bot not found.", "learning": False, "learned": False}

    knowledge = _load_knowledge(bot_id)
    history = conversation_history or []
    context = _knowledge_search(message, knowledge)

    system = config.get("system_prompt", "You are a helpful assistant.")
    if context:
        system += "\n\nRelevant knowledge:\n" + context

    messages = history[-10:] + [{"role": "user", "content": message}]

    reply = call_llm(system, messages, max_tokens=500)

    if "ONE_MOMENT_LEARNING" in reply:
        web = _search_web(message)
        if web:
            learn_system = system + "\n\nWeb search results:\n" + web
            learned_reply = call_llm(learn_system, [{"role": "user", "content": message}], max_tokens=500)

            knowledge["learned"].append({
                "question": message,
                "answer": learned_reply,
                "source": "web_search",
                "learned_at": datetime.utcnow().isoformat()
            })
            _save_knowledge(bot_id, knowledge)
            return {
                "reply": learned_reply,
                "learning": True,
                "learned": True,
                "loading_message": "One moment, learning a new skill..."
            }
        else:
            knowledge["learned"].append({
                "question": message, "answer": None,
                "source": "pending_owner",
                "learned_at": datetime.utcnow().isoformat()
            })
            _save_knowledge(bot_id, knowledge)
            return {
                "reply": "I don't have that info yet, but I've flagged it to learn. Anything else I can help with?",
                "learning": True,
                "learned": False,
                "loading_message": "One moment, learning a new skill..."
            }

    return {"reply": reply, "learning": False, "learned": False}


def add_knowledge(bot_id: str, text: str = "") -> dict:
    knowledge = _load_knowledge(bot_id)
    if text:
        existing = knowledge.get("uploaded", "")
        knowledge["uploaded"] = (existing + "\n\n" + text).strip()
        _save_knowledge(bot_id, knowledge)
    return {"added": True, "bot_id": bot_id}


def add_knowledge_from_url(bot_id: str, url: str) -> dict:
    """Scrape a URL and add its content to the bot's knowledge base."""
    text = scrape_url(url)
    if not text:
        return {"added": False, "bot_id": bot_id, "error": "Could not extract content from URL"}

    knowledge = _load_knowledge(bot_id)
    existing = knowledge.get("uploaded", "")
    knowledge["uploaded"] = (existing + "\n\n[From " + url + "]:\n" + text).strip()

    # Track sources
    if "sources" not in knowledge:
        knowledge["sources"] = []
    knowledge["sources"].append({
        "url": url,
        "scraped_at": datetime.utcnow().isoformat(),
        "chars": len(text)
    })

    _save_knowledge(bot_id, knowledge)
    return {"added": True, "bot_id": bot_id, "url": url, "chars_extracted": len(text)}


def get_pending_questions(bot_id: str) -> list:
    knowledge = _load_knowledge(bot_id)
    return [i for i in knowledge.get("learned", []) if i.get("answer") is None]
