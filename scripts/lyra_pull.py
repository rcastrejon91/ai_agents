"""
lyra_pull.py  —  Step 1 of the Lyra daily learning pipeline.

Gathers raw content from:
  Tech:     GitHub Trending (search API), HackerNews top stories
  Research: arXiv CS/AI/ML papers, arXiv physics/space/quant-ph
  Medical:  PubMed health-tech abstracts, bioRxiv biotech preprints

Outputs: /tmp/lyra_raw.json
"""

import json
import time
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
import requests

OUTPUT = Path("/tmp/lyra_raw.json")
TODAY = datetime.date.today().isoformat()
LAST_WEEK = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()

HEADERS = {"User-Agent": "LyraLearningBot/1.0 (github.com/rcastrejon91/ai_agents)"}


# ── helpers ────────────────────────────────────────────────────────────────────

def get(url: str, params: dict = None, timeout: int = 15) -> requests.Response | None:
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception as e:
        print(f"  [WARN] GET {url} failed: {e}")
        return None


def item(domain: str, title: str, url: str, snippet: str, source: str) -> dict:
    return {
        "domain": domain,
        "title": title.strip(),
        "url": url.strip(),
        "snippet": snippet.strip()[:2000],
        "source": source,
        "pulled_at": TODAY,
    }


# ── Tech: GitHub trending repos ───────────────────────────────────────────────

def pull_github_trending(limit: int = 5) -> list[dict]:
    print("  Pulling GitHub trending repos…")
    results = []
    r = get(
        "https://api.github.com/search/repositories",
        params={
            "q": f"stars:>200 created:>{LAST_WEEK}",
            "sort": "stars",
            "order": "desc",
            "per_page": limit,
        },
    )
    if not r:
        return results
    for repo in r.json().get("items", []):
        desc = repo.get("description") or ""
        topics = ", ".join(repo.get("topics", []))
        snippet = f"{desc}. Topics: {topics}. Stars: {repo['stargazers_count']}. Language: {repo.get('language','?')}."
        results.append(item("tech", repo["full_name"], repo["html_url"], snippet, "GitHub"))
    return results


# ── Tech: HackerNews top stories ──────────────────────────────────────────────

def pull_hackernews(limit: int = 7) -> list[dict]:
    print("  Pulling HackerNews top stories…")
    results = []
    r = get("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not r:
        return results
    ids = r.json()[:limit * 3]          # fetch more to filter duds
    fetched = 0
    for story_id in ids:
        if fetched >= limit:
            break
        sr = get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
        if not sr:
            continue
        story = sr.json()
        if not story or story.get("type") != "story":
            continue
        title = story.get("title", "")
        url = story.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
        score = story.get("score", 0)
        snippet = f"HN score: {score}. {story.get('text','')[:500]}"
        results.append(item("tech", title, url, snippet, "HackerNews"))
        fetched += 1
        time.sleep(0.1)
    return results


# ── Research: arXiv papers ────────────────────────────────────────────────────

def pull_arxiv(query: str, domain: str, label: str, max_results: int = 4) -> list[dict]:
    print(f"  Pulling arXiv [{label}]…")
    r = get(
        "https://export.arxiv.org/api/query",
        params={
            "search_query": query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results,
        },
    )
    if not r:
        return []

    results = []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(r.text)
    except ET.ParseError as e:
        print(f"  [WARN] arXiv XML parse error: {e}")
        return []

    for entry in root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", "", ns) or "").replace("\n", " ").strip()
        summary = (entry.findtext("atom:summary", "", ns) or "").replace("\n", " ").strip()
        link_el = entry.find("atom:id", ns)
        link = link_el.text.strip() if link_el is not None else ""
        authors = [a.findtext("atom:name", "", ns) for a in entry.findall("atom:author", ns)]
        snippet = f"Authors: {', '.join(authors[:3])}. Abstract: {summary}"
        if title:
            results.append(item(domain, title, link, snippet, f"arXiv/{label}"))

    return results


# ── Medical: PubMed recent articles ──────────────────────────────────────────

def pull_pubmed(query: str, max_results: int = 4) -> list[dict]:
    print("  Pulling PubMed…")
    BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    search = get(
        f"{BASE}/esearch.fcgi",
        params={
            "db": "pubmed",
            "term": query,
            "sort": "pub+date",
            "retmax": max_results,
            "retmode": "json",
        },
    )
    if not search:
        return []

    ids = search.json().get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    summary = get(
        f"{BASE}/esummary.fcgi",
        params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
    )
    if not summary:
        return []

    results = []
    uids = summary.json().get("result", {})
    for uid in ids:
        art = uids.get(uid, {})
        title = art.get("title", "")
        authors = [a.get("name", "") for a in art.get("authors", [])[:3]]
        pub_date = art.get("pubdate", "")
        source = art.get("source", "")
        snippet = f"Published: {pub_date}. Journal: {source}. Authors: {', '.join(authors)}."
        url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
        if title:
            results.append(item("medical", title, url, snippet, "PubMed"))

    return results


# ── Medical: bioRxiv preprints ────────────────────────────────────────────────

def pull_biorxiv(max_results: int = 3) -> list[dict]:
    print("  Pulling bioRxiv…")
    start = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
    end = TODAY
    r = get(f"https://api.biorxiv.org/details/biorxiv/{start}/{end}/0")
    if not r:
        return []

    results = []
    for paper in r.json().get("collection", [])[:max_results]:
        title = paper.get("title", "")
        abstract = paper.get("abstract", "")[:600]
        doi = paper.get("doi", "")
        url = f"https://doi.org/{doi}" if doi else "https://biorxiv.org"
        snippet = f"Abstract: {abstract}"
        if title:
            results.append(item("medical", title, url, snippet, "bioRxiv"))

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"[lyra_pull] Gathering knowledge for {TODAY}…")
    all_items: list[dict] = []

    # Tech
    all_items += pull_github_trending(5)
    all_items += pull_hackernews(7)

    # Research — AI/ML
    all_items += pull_arxiv(
        "cat:cs.AI OR cat:cs.LG OR cat:cs.CL",
        "research",
        "AI-ML",
        4,
    )
    # Research — Physics / Space / Quantum
    all_items += pull_arxiv(
        "cat:astro-ph OR cat:quant-ph OR cat:cond-mat",
        "research",
        "physics-space",
        3,
    )

    # Medical
    all_items += pull_pubmed(
        "(health technology[MeSH] OR biotech[tiab] OR digital health[tiab]) AND (2025[dp] OR 2026[dp])",
        4,
    )
    all_items += pull_biorxiv(3)

    print(f"[lyra_pull] Pulled {len(all_items)} items total.")
    OUTPUT.write_text(json.dumps(all_items, indent=2, ensure_ascii=False))
    print(f"[lyra_pull] Written → {OUTPUT}")


if __name__ == "__main__":
    main()
