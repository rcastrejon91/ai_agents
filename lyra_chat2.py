"""
lyra_chat.py — Lyra's main chat handler.
Intents:
  - build_bot       → builds a business chatbot
  - research_person → OSINT report on a person
  - research_company→ OSINT report on a company
  - search_news     → recent news search
  - scrape_url      → extract URL into active bot
  - create_tool     → Lyra writes a new Python tool and registers it
  - use_tool        → Lyra calls one of her registered custom tools
  - ask_more        → needs more info
  - chat            → general conversation
"""

import json, os
import anthropic

def _build_system_prompt() -> str:
    from tool_creator import list_tools
    tools = list_tools()
    tool_lines = ""
    if tools:
        tool_lines = "\n\nYour registered custom tools:\n" + "\n".join(
            f"  - {t['name']}: {t['description']} | params: {t['parameters']}"
            for t in tools
        )

    return """You are Lyra, an AI agent with two main capabilities:
1. Building custom chatbots for businesses
2. Conducting OSINT research using publicly available information
3. Creating and using custom tools on demand
""" + tool_lines + """

When you receive a message, respond with a JSON object:
{
  "intent": "build_bot" | "research_person" | "research_company" | "search_news" | "scrape_url" | "create_tool" | "use_tool" | "ask_more" | "chat",
  "reply": "your conversational reply",
  "business_prompt": "full business description (only if intent=build_bot)",
  "subject": "person or company name (if research intent)",
  "location": "location if mentioned (research only)",
  "extras": "any extra context like job title, company (research only)",
  "url": "url to scrape (if intent=scrape_url)",
  "news_query": "search query (if intent=search_news)",
  "tool_description": "what the new tool should do (if intent=create_tool)",
  "tool_name": "name of the registered tool to call (if intent=use_tool)",
  "tool_params": {"key": "value"} // params to pass to the tool (if intent=use_tool)
}

Rules:
- If user describes a business to build a bot for → intent: build_bot
- If user asks to research/find info about a person → intent: research_person
- If user asks to research a company/organization → intent: research_company
- If user asks for news about someone/something → intent: search_news
- If user provides a URL to add to a bot → intent: scrape_url
- If user asks you to make a new tool/skill/capability → intent: create_tool
- If user wants to use one of your registered tools → intent: use_tool
- If the message is vague, short (under 4 words), or unclear → intent: chat, reply conversationally
- Only use ask_more if you have most of what you need but are missing one specific thing
- Never use ask_more for completely ambiguous messages — use chat instead

ask_more reply style:
- Sound like a person, not a form. Bad: "Need the actual search query." Good: "What do you want me to search for?"
- One short sentence. No robotic phrasing.

Always be direct and confident. When researching, say you're on it.
Only use public information for research — make that clear."""


def lyra_chat(message: str, history: list = None, session: dict = None) -> dict:
    history = history or []
    session = session or {}

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    messages = history[-6:] + [{"role": "user", "content": message}]

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=_build_system_prompt(),
        messages=messages
    )

    raw = resp.content[0].text.strip()
    try:
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw.strip())
    except Exception:
        return {"reply": raw, "intent": "chat"}

    intent = data.get("intent", "chat")
    reply = data.get("reply", "")

    # --- Build Bot ---
    if intent == "build_bot":
        from bots.bot_builder import build_bot
        try:
            result = build_bot(data.get("business_prompt", message))
            bot_id = result["bot_id"]
            config = result["config"]
            session["last_bot_id"] = bot_id
            return {
                "reply": reply + "\n\n**Bot ID:** " + bot_id +
                         "\n**Name:** " + config.get("bot_name", "") +
                         "\n\n**Embed code:**\n" + result["embed_code"] +
                         "\n\nWant me to feed it a website URL to learn from?",
                "intent": "build_bot",
                "bot_id": bot_id,
                "embed_code": result["embed_code"],
                "config": config,
                "session": session
            }
        except Exception as e:
            return {"reply": "Error building bot: " + str(e), "intent": "error"}

    # --- Research Person ---
    if intent == "research_person":
        from osint_tools import search_person, search_social, search_news, compile_report
        subject = data.get("subject", "")
        location = data.get("location", "")
        extras = data.get("extras", "")
        if not subject:
            return {"reply": "Who do you want me to research?", "intent": "ask_more"}
        try:
            person_data = search_person(subject, location, extras)
            social_data = search_social(subject)
            news_data = search_news(subject)
            findings = {"person": person_data, "social": social_data, "news": news_data}
            report = compile_report(subject, findings, "person")
            return {
                "reply": reply + "\n\n" + report,
                "intent": "research_person",
                "subject": subject,
                "sources_found": person_data.get("sources_found", 0)
            }
        except Exception as e:
            return {"reply": "Research error: " + str(e), "intent": "error"}

    # --- Research Company ---
    if intent == "research_company":
        from osint_tools import search_company, search_news, compile_report
        subject = data.get("subject", "")
        extras = data.get("extras", "")
        if not subject:
            return {"reply": "Which company do you want me to research?", "intent": "ask_more"}
        try:
            company_data = search_company(subject, extras)
            news_data = search_news(subject)
            findings = {"company": company_data, "news": news_data}
            report = compile_report(subject, findings, "company")
            return {
                "reply": reply + "\n\n" + report,
                "intent": "research_company",
                "subject": subject
            }
        except Exception as e:
            return {"reply": "Research error: " + str(e), "intent": "error"}

    # --- News Search ---
    if intent == "search_news":
        from osint_tools import search_news
        query = data.get("news_query", message)
        try:
            results = search_news(query)
            articles = results.get("articles", [])
            formatted = "\n\n".join(
                "**" + a.get("title", "") + "**\n" + a.get("snippet", "") + "\n" + a.get("url", "")
                for a in articles[:5]
            )
            return {
                "reply": reply + "\n\n" + formatted,
                "intent": "search_news",
                "count": len(articles)
            }
        except Exception as e:
            return {"reply": "News search error: " + str(e), "intent": "error"}

    # --- Scrape URL into active bot ---
    if intent == "scrape_url":
        url = data.get("url", "")
        active_bot_id = session.get("last_bot_id")
        if url and active_bot_id:
            from bots.base_bot import add_knowledge_from_url
            try:
                result = add_knowledge_from_url(active_bot_id, url)
                return {
                    "reply": reply + "\n\nScraped " + str(result.get("chars_extracted", 0)) + " chars from " + url + " — added to your bot.",
                    "intent": "scrape_url",
                    "session": session
                }
            except Exception as e:
                return {"reply": "Couldn't scrape that URL: " + str(e), "intent": "error"}
        elif url and not active_bot_id:
            return {"reply": "Tell me about the business first and I'll build the bot, then add the URL.", "intent": "ask_more"}

    # --- Create a new tool ---
    if intent == "create_tool":
        from tool_creator import create_tool
        description = data.get("tool_description", message)
        try:
            result = create_tool(description)
            return {
                "reply": reply + "\n\n**New tool created:** `" + result["name"] + "`\n"
                         + result["description"] + "\n"
                         + ("**Params:** " + str(result["parameters"]) if result["parameters"] else "No params needed."),
                "intent": "create_tool",
                "tool": result,
            }
        except Exception as e:
            return {"reply": "Couldn't create that tool: " + str(e), "intent": "error"}

    # --- Use a registered tool ---
    if intent == "use_tool":
        from tool_creator import run_tool, list_tools
        tool_name = data.get("tool_name", "")
        tool_params = data.get("tool_params", {})
        if not tool_name:
            tools = list_tools()
            names = [t["name"] for t in tools]
            return {"reply": "Which tool? I have: " + ", ".join(names) if names else "No tools registered yet.", "intent": "ask_more"}
        try:
            result = run_tool(tool_name, tool_params)
            if "error" in result:
                return {"reply": "Tool error: " + result["error"], "intent": "error"}
            return {
                "reply": reply + "\n\n**" + tool_name + " result:**\n" + json.dumps(result, indent=2),
                "intent": "use_tool",
                "tool_name": tool_name,
                "tool_result": result,
            }
        except Exception as e:
            return {"reply": "Couldn't run tool `" + tool_name + "`: " + str(e), "intent": "error"}

    return {"reply": reply, "intent": intent}
