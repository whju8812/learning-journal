import pytest
from app import app, _text, LEARNING_DIRECTIONS, SOURCES
import xml.etree.ElementTree as ET


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "學習" in resp.data.decode("utf-8")


def test_api_news_returns_json(client):
    resp = client.get("/api/news")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_api_learning_returns_all_directions(client):
    resp = client.get("/api/learning")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 5
    titles = [d["title"] for d in data]
    assert "AI / 機器學習" in titles
    assert "前端開發" in titles


def test_text_helper():
    xml = '<root><title>Hello</title><desc>World</desc></root>'
    el = ET.fromstring(xml)
    assert _text(el, "title") == "Hello"
    assert _text(el, "missing") == ""


# ─── /api/entries/search ────────────────────────────────────────────────

def test_search_empty_query_returns_empty_results(client):
    resp = client.get("/api/entries/search?q=")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["query"] == ""
    assert data["results"] == []


def test_search_no_supabase_returns_empty(client, monkeypatch):
    import app as app_mod
    monkeypatch.setattr(app_mod, "supabase", None)
    resp = client.get("/api/entries/search?q=hello")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["query"] == "hello"
    assert data["results"] == []


def test_search_matches_tech_content(client, monkeypatch):
    """Search should find a row whose tech_content contains the term."""
    import app as app_mod

    rows = [
        {
            "entry_date": "2026-05-18",
            "session_label": "08:00",
            "tech_content": "今天介紹 LangChain 的最新版本。",
            "tech_application": "適合工程師上手 chatbot。",
            "learning_analysis": {"AI / 機器學習": {"summary": "x", "items": []}},
            "sources": [{"title": "Other", "url": "https://example.com"}],
        },
        {
            "entry_date": "2025-12-30",
            "session_label": "20:00",
            "tech_content": "Kubernetes 1.30 釋出。",
            "tech_application": "",
            "learning_analysis": {},
            "sources": [],
        },
    ]

    class _R:
        def __init__(self, data): self.data = data
    class _Q:
        def __init__(self, data): self._data = data
        def select(self, *a, **k): return self
        def order(self, *a, **k):  return self
        def execute(self):         return _R(self._data)
    class _C:
        def table(self, name): return _Q(rows)

    monkeypatch.setattr(app_mod, "supabase", _C())
    resp = client.get("/api/entries/search?q=LangChain")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 1
    assert data["results"][0]["entry_date"] == "2026-05-18"
    assert data["results"][0]["matched_field"] == "技術內容"
    assert "LangChain" in data["results"][0]["snippet"]


def test_search_route_resolves_before_date_str(client):
    """Critical: /api/entries/search must NOT be parsed as a date."""
    resp = client.get("/api/entries/search?q=anything")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "results" in body
