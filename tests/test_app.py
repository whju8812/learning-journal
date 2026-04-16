import pytest
from app import app, _text, _strip_tags, LEARNING_DIRECTIONS, SOURCES
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


def test_strip_tags():
    assert _strip_tags("<p>Hello <b>World</b></p>") == "Hello "
    assert _strip_tags("") == ""
