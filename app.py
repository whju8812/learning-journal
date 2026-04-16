import os
import json
import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

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
    "atom": "http://www.w3.org/2005/Atom",
    "dc": "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
}


def _text(el, *tags):
    """Return stripped text of the first matching child tag."""
    for tag in tags:
        child = el.find(tag, NS)
        if child is not None and child.text:
            return child.text.strip()
    return ""


def _strip_tags(s):
    try:
        return ET.fromstring(f"<x>{s}</x>").itertext().__next__()
    except Exception:
        return s[:200] if s else ""


def fetch_rss(name, source):
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        # RSS 2.0
        channel = root.find("channel")
        if channel is not None:
            entries = channel.findall("item")
        else:
            # Atom feed
            entries = root.findall("{http://www.w3.org/2005/Atom}entry")

        items = []
        for entry in entries[:8]:
            # title
            title = (
                _text(entry, "title", "{http://www.w3.org/2005/Atom}title") or "無標題"
            )[:120]

            # link
            link = _text(entry, "link", "guid")
            if not link:
                a_link = entry.find("{http://www.w3.org/2005/Atom}link")
                link = (a_link.get("href", "#") if a_link is not None else "#")

            # date
            date_str = _text(
                entry,
                "pubDate",
                "published",
                "{http://www.w3.org/2005/Atom}published",
                "{http://www.w3.org/2005/Atom}updated",
            )[:16]

            items.append({"title": title, "url": link, "summary": "", "date": date_str})

        return name, source, items
    except Exception:
        return name, source, []


def fetch_github_trending(name, source):
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        url = source["url"].replace("{date}", today)
        resp = requests.get(
            url,
            headers={**HEADERS, "Accept": "application/vnd.github+json"},
            timeout=10,
        )
        data = resp.json()
        items = [
            {
                "title": repo.get("full_name", ""),
                "url": repo.get("html_url", "#"),
                "summary": (repo.get("description") or "")[:200],
                "date": repo.get("created_at", "")[:10],
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language") or "N/A",
            }
            for repo in data.get("items", [])[:8]
        ]
        return name, source, items
    except Exception:
        return name, source, []


def fetch_all_sources():
    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [
            executor.submit(
                fetch_rss if src["type"] == "rss" else fetch_github_trending,
                name,
                src,
            )
            for name, src in SOURCES.items()
        ]
        for future in as_completed(futures):
            name, source, items = future.result()
            results.append(
                {
                    "name": name,
                    "icon": source["icon"],
                    "category": source["category"],
                    "url": source["url"].split("?")[0],
                    "items": items,
                    "count": len(items),
                }
            )
    results.sort(key=lambda x: x["name"])
    return results


@app.route("/")
def index():
    today = datetime.now().strftime("%Y 年 %m 月 %d 日")
    return render_template("index.html", today=today, learning_directions=LEARNING_DIRECTIONS)


@app.route("/api/news")
def api_news():
    return jsonify(fetch_all_sources())


@app.route("/api/learning")
def api_learning():
    return jsonify(LEARNING_DIRECTIONS)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
