import json
import logging
import os
import pathlib
import re
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText

import requests
import yaml
from bs4 import BeautifulSoup

# ---- Setup logging ----
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("data/lyra_learning.log", mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# Ensure data directory exists
os.makedirs("data", exist_ok=True)


def validate_email(email):
    """Validate email address format."""
    if not isinstance(email, str) or not email:
        return False

    # Simple email validation regex
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email)) and len(email) <= 254


def get_utc_timestamp():
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)


def format_datetime(dt_obj):
    """Format datetime object to string with UTC indicator."""
    if dt_obj.tzinfo is None:
        # Assume naive datetime is UTC
        dt_obj = dt_obj.replace(tzinfo=timezone.utc)
    return dt_obj.strftime("%Y-%m-%d %H:%M:%S UTC")


def get_utc_date_string():
    """Get current date in UTC as string."""
    return get_utc_timestamp().strftime("%Y-%m-%d")


# ---- Paths / Config
MEM_PATH = "data/lyra_memory.json"
TOPIC_CONFIG_FILE = "topics.yml"
SEED_URLS = [
    "https://www.bbc.com/news",
    "https://www.scientificamerican.com/",
    "https://techcrunch.com/",
]

# ---- Secrets
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_FROM = os.getenv("EMAIL_FROM")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_OPENAI = bool(OPENAI_API_KEY)

# ---- Load topic/safety/robotics config
ALLOW_TOPICS = [
    "health",
    "medicine",
    "nursing",
    "hospital",
    "public health",
    "ai",
    "machine learning",
    "accessibility",
    "assistive",
    "security",
    "privacy",
    "ethics",
    "education",
    "productivity",
]
DENY_TOPICS = [
    "celebrity",
    "gossip",
    "rumor",
    "leak",
    "nsfw",
    "sports scandal",
    "casino",
    "get rich quick",
]
BLOCK_WORDS = ["slur1", "slur2", "extreme phrase"]
SAFETY = {}
ROBOTICS_POLICY = {}


def load_topic_cfg():
    global ALLOW_TOPICS, DENY_TOPICS, BLOCK_WORDS, SAFETY, ROBOTICS_POLICY
    if os.path.exists(TOPIC_CONFIG_FILE):
        try:
            cfg = yaml.safe_load(open(TOPIC_CONFIG_FILE, "r", encoding="utf-8")) or {}
            ALLOW_TOPICS = cfg.get("allow_topics", ALLOW_TOPICS)
            DENY_TOPICS = cfg.get("deny_topics", DENY_TOPICS)
            BLOCK_WORDS = cfg.get("block_words", BLOCK_WORDS)
            SAFETY = cfg.get("safety", {})
            ROBOTICS_POLICY = cfg.get("robotics", {}) or {}
        except Exception as e:
            print("⚠ topics.yml load failed:", e)


load_topic_cfg()


# ==== Memory ====
def load_memory():
    if not os.path.exists(MEM_PATH):
        return []
    try:
        return json.load(open(MEM_PATH, "r", encoding="utf-8"))
    except:
        return []


def save_memory(mem):
    os.makedirs(os.path.dirname(MEM_PATH), exist_ok=True)
    json.dump(
        mem[-200:], open(MEM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2
    )


# ==== Fetch + Filter ====
def fetch_sources():
    chunks = []
    for url in SEED_URLS:
        try:
            r = requests.get(url, timeout=12, headers={"User-Agent": "Lyra/1.0"})
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            text = " ".join(
                p.get_text(" ", strip=True) for p in soup.find_all("p")[:10]
            )
            if text:
                chunks.append({"url": url, "text": text[:4000]})
        except Exception as e:
            chunks.append({"url": url, "error": str(e)})
    return chunks


def matches_any(text, needles):
    low = text.lower()
    return any(n in low for n in needles)


def filter_chunks(chunks):
    kept, skipped = [], []
    for c in chunks:
        if "error" in c:
            skipped.append(c | {"reason": f"fetch error: {c['error']}"})
            continue
        t = c["text"]
        if matches_any(t, DENY_TOPICS):
            skipped.append(c | {"reason": "deny-topic"})
            continue
        if ALLOW_TOPICS and not matches_any(t, ALLOW_TOPICS):
            skipped.append(c | {"reason": "not in allow list"})
            continue
        kept.append(c)
    return kept, skipped


def safe_scrub(text):
    out = text
    for w in BLOCK_WORDS:
        out = re.sub(re.escape(w), "[filtered]", out, flags=re.IGNORECASE)
    return out


# ==== Summarize + Glossary ====
JARGON_RE = re.compile(
    r"\b([A-Z][a-zA-Z0-9\-]{2,}(?:\s+[A-Z][a-zA-Z0-9\-]{2,}){0,2})\b"
)


def extract_terms(text, n=10):
    counts = {}
    for m in JARGON_RE.findall(text):
        k = m.strip()
        if k.lower() in {"the", "and", "for", "with", "from", "this", "that"}:
            continue
        counts[k] = counts.get(k, 0) + 1
    return [w for w, _ in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]]


def summarize_simple(chunks, prev_plan):
    lines = [f"- {c['url']}" for c in chunks]
    return {
        "summary": "Fetched sources:\n" + "\n".join(lines),
        "insights": ["Basic ingestion only (no model key set)."],
        "next_plan": (
            prev_plan[:3] if prev_plan else ["Deep-dive one allow-listed source"]
        ),
    }


def summarize_with_openai(chunks, memory):
    import openai

    openai.api_key = OPENAI_API_KEY
    last_plan = memory[-1].get("next_plan", [])[:5] if memory else []
    text_blocks = [f"Source: {c['url']}\nExcerpt: {c['text']}" for c in chunks]
    corpus = "\n\n".join(tb[:3500] for tb in text_blocks)
    prompt = f"""You are Lyra. From the excerpts, produce:
1) 6 concise neutral bullets of today’s learning,
2) 3–5 actionable insights,
3) 3–5 items for 'next_plan' considering prior plan: {last_plan}.
Avoid offensive language and speculation.
TEXT:
{corpus}"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Concise daily learner."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    out = resp.choices[0].message["content"]
    insights, next_plan = [], []
    for line in out.splitlines():
        s = line.strip(" -•\t")
        if not s:
            continue
        if any(k in s.lower() for k in ["tomorrow", "next", "plan"]):
            next_plan.append(s)
        else:
            insights.append(s)
    return {
        "summary": out[:1200],
        "insights": insights[:8],
        "next_plan": (next_plan or ["Return to a medical/AI source"])[:5],
    }


def define_with_openai(terms, context):
    import openai

    openai.api_key = OPENAI_API_KEY
    prompt = f"""Give short, friendly, non-technical definitions for these terms (1–2 sentences), grounded only in the context.
Terms: {terms}
Context:
{context[:6000]}"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Helpful glossary generator."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message["content"]


# ==== Robotics sandbox (text-only, safe) ====
def robotics_brainstorm(kept, policy, use_openai):
    corpus = " ".join(c.get("text", "") for c in kept)[:5000].lower()
    for bad in policy.get("banned_terms", []):
        corpus = corpus.replace(bad.lower(), "[filtered]")
    focus = (policy.get("focus") or ["assistive/rehab"])[0]
    max_torque = float(policy.get("actuator_limits", {}).get("max_torque_Nm", 2.0))
    max_speed = float(policy.get("actuator_limits", {}).get("max_speed_mps", 0.5))
    materials = policy.get("materials_whitelist", ["PLA", "PETG", "TPU"])
    proposal = {
        "concept": f"{focus.title()} bot: small wheeled platform with tablet/voice for navigation help.",
        "safety_limits": {
            "max_speed_mps": max_speed,
            "max_joint_torque_Nm": max_torque,
            "materials_only": materials,
            "no_hazardous_functions": True,
            "human_approval_required": True,
        },
        "modules": [
            "2‑wheel base + caster",
            "SBC + mic array",
            "USB depth/RGB cam",
            "Speakers + TTS",
            "8–10'' tablet UI",
        ],
        "printables": [
            "chassis plates (PLA/PETG)",
            "sensor mast (TPU coupler)",
            "tablet bracket",
            "cable guides",
        ],
        "notes": "No doors/elevators actuation; **no** medical device interaction; indoor demo only.",
    }
    if use_openai:
        try:
            import json as _json

            import openai

            openai.api_key = OPENAI_API_KEY
            system = (
                f"Safety-first robotics planner. Propose a single small, low-power, indoor assistive concept. "
                f"Speed ≤ {max_speed} m/s, torque ≤ {max_torque} Nm, materials {materials}. No dangerous content."
            )
            user = f"Context: {corpus[:2000]}"
            res = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
            )
            try:
                proposal = _json.loads(res.choices[0].message["content"])
            except:
                pass
        except:
            pass
    text = json.dumps(proposal, ensure_ascii=False)
    for bad in policy.get("banned_terms", []):
        text = re.sub(re.escape(bad), "[filtered]", text, flags=re.IGNORECASE)
    return text


# ==== Email + telemetry helpers ====
def read_last_lines(path, n=20):
    try:
        return open(path, "r", encoding="utf-8").read().splitlines()[-n:]
    except:
        return []


def summarize_admin_mode_events():
    p = pathlib.Path("data/admin_mode.log")
    lines = read_last_lines(str(p), 20)
    if not lines:
        return "(no recent admin mode events)"
    out = []
    for ln in lines:
        try:
            ev = json.loads(ln)
            t = ev.get("type", "event")
            if t == "admin_mode_update":
                b, a = ev.get("before", {}), ev.get("after", {})
                out.append(
                    f"- mode: {b.get('admin')}→{a.get('admin')}, persona: {b.get('personality')}→{a.get('personality')} (via {ev.get('used')})"
                )
            elif t == "auth_failed":
                out.append(f"- auth failed (via {ev.get('used')})")
        except:
            pass
    return "\n".join(out) if out else "(no recent admin mode events)"


def summarize_pitch_history():
    p = pathlib.Path("data/pitches.json")
    if not p.exists():
        return "(no pitch decisions yet)"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        hist = data.get("history", [])[-10:]
        if not hist:
            return "(no pitch decisions yet)"
        return "\n".join(
            f"- [{h.get('decision','?').upper()}] {h.get('title','(untitled)')} (id {h.get('id')})"
            for h in hist
        )
    except:
        return "(could not read pitch history)"


def make_email_body(entry, safety_audit: str, admin_summary: str, pitches_summary: str):
    parts = (
        [
            f"👋 Lyra Daily Learning — {entry['date']}",
            "",
            "Summary:",
            safe_scrub(entry["summary"]),
            "",
            "Insights:",
        ]
        + [f"• {safe_scrub(i)}" for i in entry["insights"]]
        + [
            "",
            "Jargon Glossary:",
        ]
        + ([f"• {g}" for g in entry.get("glossary", ["(none today)"])])
        + [
            "",
            "Tomorrow’s Plan:",
        ]
        + [f"• {safe_scrub(p)}" for p in entry["next_plan"]]
        + [
            "",
            "Sources (kept):",
        ]
        + [f"• {s['url']}" for s in entry["sources_kept"]]
        + [
            "",
            "Skipped sources (reason):",
        ]
        + [
            f"• {s['url']} — {s.get('reason','')}"
            for s in entry.get("sources_skipped", [])
        ]
        + [
            "",
            "Robotics Sandbox (requires human approval):",
            entry.get("robotics_sandbox", "(disabled)"),
        ]
        + [
            "",
            "Self‑Repair Status:",
            entry.get("self_repair_status", "(robot_core not reachable)"),
        ]
        + [
            "",
            "Safety Report (last 20 events):",
            safety_audit or "(no recent safety events)",
        ]
        + [
            "",
            "Admin Mode Activity (last ~20 events):",
            admin_summary,
            "",
            "Pitch Decisions (last 10):",
            pitches_summary,
        ]
    )
    return "\n".join(parts)


def send_email(subject, body):
    """Send email with proper error handling and validation."""
    try:
        # Validate email configuration
        if not all([SMTP_HOST, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO]):
            logger.error(
                "Email configuration incomplete. Check SMTP_HOST, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO environment variables."
            )
            return False

        # Validate email addresses
        if not validate_email(EMAIL_FROM):
            logger.error(f"Invalid sender email address: {EMAIL_FROM}")
            return False

        if not validate_email(EMAIL_TO):
            logger.error(f"Invalid recipient email address: {EMAIL_TO}")
            return False

        # Create message
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg["Date"] = format_datetime(get_utc_timestamp())

        # Send email
        logger.info(f"Sending email to {EMAIL_TO}: {subject}")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)

        logger.info("Email sent successfully")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {str(e)}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"SMTP recipients refused: {str(e)}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {str(e)}")
        return False


# ==== Main ====
if __name__ == "__main__":
    try:
        logger.info("Starting Lyra learning process")

        # Load memory and fetch sources
        logger.info("Loading memory and fetching sources")
        memory = load_memory()
        raw = fetch_sources()
        kept, skipped = filter_chunks(raw)

        logger.info(
            f"Fetched {len(raw)} sources, kept {len(kept)}, skipped {len(skipped)}"
        )

        if not kept:
            logger.warning("No sources kept after filtering, using first 2 raw sources")
            kept = [c for c in raw if "error" not in c][:2]

        # Analysis phase
        logger.info("Analyzing sources")
        if USE_OPENAI:
            analysis = summarize_with_openai(kept, memory)
        else:
            prev = [i for e in memory for i in e.get("next_plan", [])]
            analysis = summarize_simple(kept, prev)

        # Glossary generation
        logger.info("Generating glossary")
        combined = " ".join(c.get("text", "") for c in kept)[:12000]
        terms = extract_terms(combined, 10)
        if terms and USE_OPENAI:
            try:
                gloss = [
                    g.strip()
                    for g in define_with_openai(terms, combined).splitlines()
                    if g.strip()
                ]
            except Exception as e:
                logger.warning(f"Failed to generate glossary with OpenAI: {str(e)}")
                gloss = [f"{t}: (definition unavailable)" for t in terms]
        elif terms:
            gloss = [
                f"{t}: (definition pending — no model key set)" for t in terms
            ]  # fallback
        else:
            gloss = []

        # Robotics brainstorming (double gate)
        logger.info("Processing robotics sandbox")
        robotics_enabled = bool(ROBOTICS_POLICY.get("enabled")) and os.getenv(
            "ROBOTICS_ENABLE", "0"
        ).lower() in {"1", "true", "yes"}

        if robotics_enabled:
            try:
                robotics_section = robotics_brainstorm(
                    kept, ROBOTICS_POLICY, USE_OPENAI
                )
            except Exception as e:
                logger.warning(f"Robotics brainstorm failed: {str(e)}")
                robotics_section = "(robotics brainstorm failed)"
        else:
            robotics_section = "(disabled)"

        # Self-repair status (call robot_core if running)
        logger.info("Checking self-repair status")
        try:
            diag = requests.post(
                os.getenv("ROBOT_CORE_URL", "http://localhost:8088")
                + "/robot/diagnose",
                timeout=3,
            ).json()
            plan = requests.post(
                os.getenv("ROBOT_CORE_URL", "http://localhost:8088")
                + "/robot/repair/plan",
                timeout=5,
            ).json()
            self_repair = f"Diagnostic: {'OK' if diag.get('ok') else 'Issues found'}; Steps: {len(plan.get('steps',[]))}; Approval required: {plan.get('requires_approval', True)}"
        except Exception as e:
            logger.info(f"Robot core not reachable: {str(e)}")
            self_repair = f"(robot_core not reachable: {e})"

        # Create learning entry
        logger.info("Creating learning entry")
        entry = {
            "date": get_utc_date_string(),
            "timestamp": get_utc_timestamp().isoformat(),
            "summary": analysis["summary"],
            "insights": analysis["insights"],
            "next_plan": analysis["next_plan"],
            "glossary": gloss[:12],
            "sources_kept": kept,
            "sources_skipped": skipped,
            "robotics_sandbox": robotics_section,
            "self_repair_status": self_repair,
        }

        memory.append(entry)

        # Save memory with error handling
        try:
            save_memory(memory)
            logger.info("Memory saved successfully")
        except Exception as e:
            logger.error(f"Failed to save memory: {str(e)}")
            raise

        # Generate audit reports
        logger.info("Generating audit reports")
        try:
            safety_audit = (
                "\n".join(read_last_lines("data/robot_audit.log", 20)) or "(none)"
            )
        except Exception as e:
            logger.warning(f"Failed to read safety audit: {str(e)}")
            safety_audit = "(audit log unavailable)"

        admin_summary = summarize_admin_mode_events()
        pitches_summary = summarize_pitch_history()

        # Send email report
        logger.info("Sending email report")
        body = make_email_body(entry, safety_audit, admin_summary, pitches_summary)

        if send_email("Lyra Daily Learning Update", body):
            logger.info("Learning process completed successfully")
            print(
                "✅ Learning process completed successfully. Email sent; memory updated."
            )
        else:
            logger.warning("Email sending failed, but learning process completed")
            print(
                "⚠️ Learning process completed but email sending failed. Memory updated."
            )

    except KeyboardInterrupt:
        logger.info("Learning process interrupted by user")
        print("⏹️ Learning process interrupted by user")
    except Exception as e:
        logger.error(f"Learning process failed: {str(e)}", exc_info=True)
        print(f"❌ Learning process failed: {str(e)}")
        raise
