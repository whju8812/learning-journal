import os
import secrets
import time
import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timezone, date as date_type
from flask import Flask, render_template, jsonify, request
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# ─── Supabase ───
SUPABASE_URL    = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY    = os.environ.get("SUPABASE_KEY", "")
JOURNAL_API_KEY = os.environ.get("JOURNAL_API_KEY", "")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        pass

VALID_SESSION_LABELS = {"01:00", "04:00", "07:00", "10:00"}
REQUIRED_DIRECTIONS = {
    "AI / 機器學習",
    "雲端與基礎架構",
    "前端開發",
    "後端 / 系統設計",
    "開發者工具 / DevOps",
}

# ─── RSS sources ───
SOURCES = {
    "Hacker News": {
        "url": "https://news.ycombinator.com/rss",
        "type": "rss",
        "category": "社群技術討論",
        "icon": "🔶",
    },
    "The Verge - Tech": {
        "url": "https://www.theverge.com/tech/rss/index.xml",
        "type": "rss",
        "category": "科技新聞",
        "icon": "🔷",
    },
    "InfoQ": {
        "url": "https://feed.infoq.com",
        "type": "rss",
        "category": "軟體工程",
        "icon": "🟦",
    },
    "Dev.to": {
        "url": "https://dev.to/feed",
        "type": "rss",
        "category": "開發者文章",
        "icon": "💻",
    },
    "GitHub Trending": {
        "url": "https://api.github.com/search/repositories?q=created:>{date}+stars:>50&sort=stars&order=desc&per_page=10",
        "type": "github",
        "category": "開源趨勢",
        "icon": "⭐",
    },
}

LEARNING_DIRECTIONS = [
    {
        "title": "AI / 機器學習",
        "icon": "🤖",
        "topics": ["LLM 應用開發", "RAG 架構", "向量資料庫", "Fine-tuning 技術"],
        "resources": ["papers.arxiv.org", "huggingface.co", "fast.ai"],
    },
    {
        "title": "雲端與基礎架構",
        "icon": "☁️",
        "topics": ["Kubernetes / Container", "Serverless 架構", "Edge Computing", "IaC (Terraform)"],
        "resources": ["cloud.google.com/blog", "aws.amazon.com/blogs", "azure.microsoft.com/blog"],
    },
    {
        "title": "前端開發",
        "icon": "🎨",
        "topics": ["React / Next.js", "WebAssembly", "Performance Optimization", "Web Components"],
        "resources": ["web.dev", "developer.mozilla.org", "css-tricks.com"],
    },
    {
        "title": "後端 / 系統設計",
        "icon": "⚙️",
        "topics": ["分散式系統", "API 設計", "資料庫優化", "安全性強化"],
        "resources": ["highscalability.com", "martinfowler.com", "databasedesign.org"],
    },
    {
        "title": "開發者工具 / DevOps",
        "icon": "🛠️",
        "topics": ["CI/CD Pipeline", "可觀測性 (Observability)", "Git 工作流", "程式碼品質"],
        "resources": ["github.blog", "about.gitlab.com/blog", "devops.com"],
    },
]

HEADERS = {"User-Agent": "LearningJournal/1.0 (+https://github.com)"}
NS = {
    "atom":    "http://www.w3.org/2005/Atom",
    "dc":      "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
}

# ─── RSS cache (5-minute TTL) ───
_news_cache      = None
_news_cache_time = 0.0
_NEWS_CACHE_TTL  = 300


def _text(el, *tags):
    for tag in tags:
        child = el.find(tag, NS)
        if child is not None and child.text:
            return child.text.strip()
    return ""


def fetch_rss(name, source):
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        channel = root.find("channel")
        entries = channel.findall("item") if channel is not None \
            else root.findall("{http://www.w3.org/2005/Atom}entry")

        items = []
        for entry in entries[:8]:
            title = (_text(entry, "title", "{http://www.w3.org/2005/Atom}title") or "無標題")[:120]
            link  = _text(entry, "link", "guid")
            if not link:
                a_link = entry.find("{http://www.w3.org/2005/Atom}link")
                link   = a_link.get("href", "#") if a_link is not None else "#"
            date_str = _text(
                entry, "pubDate", "published",
                "{http://www.w3.org/2005/Atom}published",
                "{http://www.w3.org/2005/Atom}updated",
            )[:16]
            items.append({"title": title, "url": link, "date": date_str})

        return name, source, items
    except Exception:
        return name, source, []


def fetch_github_trending(name, source):
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        url   = source["url"].replace("{date}", today)
        resp  = requests.get(url, headers={**HEADERS, "Accept": "application/vnd.github+json"}, timeout=10)
        data  = resp.json()
        items = [
            {
                "title":    repo.get("full_name", ""),
                "url":      repo.get("html_url", "#"),
                "date":     repo.get("created_at", "")[:10],
                "stars":    repo.get("stargazers_count", 0),
                "language": repo.get("language") or "N/A",
                "summary":  (repo.get("description") or "")[:200],
            }
            for repo in data.get("items", [])[:8]
        ]
        return name, source, items
    except Exception:
        return name, source, []


def _fetch_all_sources():
    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [
            executor.submit(
                fetch_rss if src["type"] == "rss" else fetch_github_trending,
                name, src,
            )
            for name, src in SOURCES.items()
        ]
        for future in as_completed(futures):
            name, source, items = future.result()
            results.append({
                "name":     name,
                "icon":     source["icon"],
                "category": source["category"],
                "url":      source["url"].split("?")[0],
                "items":    items,
                "count":    len(items),
            })
    results.sort(key=lambda x: x["name"])
    return results


def fetch_all_sources_cached():
    global _news_cache, _news_cache_time
    now = time.monotonic()
    if _news_cache is None or now - _news_cache_time > _NEWS_CACHE_TTL:
        _news_cache      = _fetch_all_sources()
        _news_cache_time = now
    return _news_cache


# ─── Page routes ───

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


# ─── API routes ───

@app.route("/api/news")
def api_news():
    return jsonify(fetch_all_sources_cached())


@app.route("/api/learning")
def api_learning():
    return jsonify(LEARNING_DIRECTIONS)


# ─── Journal routes ───
# IMPORTANT: /api/entries/health must be registered BEFORE /api/entries/<date_str>
# Flask matches routes in registration order — "health" would be treated as a date
# string if <date_str> is registered first.

def _auth_error():
    provided = request.headers.get("X-Journal-Key", "")
    if not JOURNAL_API_KEY or not secrets.compare_digest(provided, JOURNAL_API_KEY):
        return jsonify({"error": "Unauthorized"}), 401
    return None


@app.route("/api/entries/health")
def api_journal_health():
    OVERDUE_RESPONSE = {"last_entry_date": None, "last_session_label": None, "days_since_last_entry": None, "is_overdue": True}
    if supabase is None:
        return jsonify(OVERDUE_RESPONSE), 200
    try:
        result = (
            supabase.table("journal_entries")
            .select("entry_date, session_label, created_at")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if not result.data:
            return jsonify(OVERDUE_RESPONSE), 200
        row       = result.data[0]
        last_date = date_type.fromisoformat(row["entry_date"])
        delta     = (date_type.today() - last_date).days
        return jsonify({
            "last_entry_date":     row["entry_date"],
            "last_session_label":  row["session_label"],
            "days_since_last_entry": delta,
            "is_overdue":          delta > 0,
        }), 200
    except Exception:
        return jsonify(OVERDUE_RESPONSE), 200


@app.route("/api/entries")
def api_journal_list():
    if supabase is None:
        return jsonify([]), 200
    try:
        result = (
            supabase.table("journal_entries")
            .select("entry_date, created_at")
            .order("entry_date", desc=True)
            .execute()
        )
        seen = {}
        for row in result.data:
            d = row["entry_date"]
            if d not in seen:
                seen[d] = row["created_at"]
        return jsonify([{"entry_date": d, "created_at": seen[d]} for d in seen]), 200
    except Exception:
        return jsonify([]), 200


@app.route("/api/entries/<date_str>")
def api_journal_entry(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format, expected YYYY-MM-DD"}), 400
    if supabase is None:
        return jsonify({"error": "Database not configured"}), 503
    try:
        result = (
            supabase.table("journal_entries")
            .select("*")
            .eq("entry_date", date_str)
            .order("session_label")
            .execute()
        )
        if not result.data:
            return jsonify({"error": "Not found"}), 404
        return jsonify(result.data), 200
    except Exception:
        return jsonify({"error": "Service unavailable"}), 503


@app.route("/api/entries", methods=["POST"])
def api_journal_post():
    err = _auth_error()
    if err:
        return err

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    entry_date        = (data.get("entry_date") or "").strip()
    session_label     = (data.get("session_label") or "").strip()
    tech_content      = (data.get("tech_content") or "").strip()
    learning_analysis = data.get("learning_analysis")
    sources           = data.get("sources", [])

    if not entry_date or not session_label or not tech_content or not learning_analysis:
        return jsonify({"error": "Missing required fields: entry_date, session_label, tech_content, learning_analysis"}), 400

    try:
        datetime.strptime(entry_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid entry_date format, expected YYYY-MM-DD"}), 400

    if session_label not in VALID_SESSION_LABELS:
        return jsonify({"error": f"Invalid session_label — must be one of: {', '.join(sorted(VALID_SESSION_LABELS))}"}), 400

    if not isinstance(learning_analysis, dict):
        return jsonify({"error": "learning_analysis must be an object"}), 400

    if set(learning_analysis.keys()) != REQUIRED_DIRECTIONS:
        return jsonify({"error": "learning_analysis must contain exactly the 5 required directions"}), 400

    for direction, val in learning_analysis.items():
        if not isinstance(val, dict) or "summary" not in val or "items" not in val:
            return jsonify({"error": f"Direction '{direction}' must have 'summary' and 'items'"}), 400
        if not val["summary"]:
            return jsonify({"error": f"Direction '{direction}' summary cannot be empty"}), 400

    if supabase is None:
        return jsonify({"error": "Database not configured"}), 503

    try:
        result = supabase.table("journal_entries").insert({
            "entry_date":        entry_date,
            "session_label":     session_label,
            "tech_content":      tech_content,
            "learning_analysis": learning_analysis,
            "sources":           sources,
        }).execute()
        return jsonify({"ok": True, "id": result.data[0]["id"]}), 201
    except Exception as e:
        err_str = str(e).lower()
        if "unique" in err_str or "duplicate" in err_str or "23505" in err_str or "conflict" in err_str:
            return jsonify({"error": "Entry already exists for this date and session"}), 409
        return jsonify({"error": "Service unavailable"}), 503


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
