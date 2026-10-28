"""Общие фикстуры для тестов: TestClient и мок-заменитель Open Library.

Реальные HTTP-запросы к Open Library не выполняются: обращение к внешнему API
подменяется асинхронной заглушкой ``_fetch_json``.
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main

FICTION_WORKS = [
    {
        "title": "The Great Gatsby",
        "authors": [{"name": "F. Scott Fitzgerald"}],
        "cover_id": 12345,
        "description": "A novel about the American dream.",
    },
    {"title": "No Cover Book", "authors": [], "cover_id": None},
]

AUTHOR_DOCS = [
    {
        "title": "The Great Gatsby",
        "author_name": ["F. Scott Fitzgerald"],
        "cover_i": 12345,
        "first_sentence": ["In my younger and more vulnerable years..."],
    },
    {"title": "Tender Is the Night", "author_name": ["F. Scott Fitzgerald"]},
]


@pytest.fixture(autouse=True)
def _clear_popular_cache():
    """Сбрасывает кеш популярных книг до и после каждого теста."""
    main._popular_cache = None
    yield
    main._popular_cache = None


@pytest.fixture
def client():
    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture
def mock_open_library(monkeypatch):
    """Подменяет запросы к Open Library и считает их количество."""
    calls = {"count": 0}

    async def fake_fetch_json(path, params=None):
        calls["count"] += 1
        if path.startswith("/subjects/"):
            return {"works": FICTION_WORKS}
        if path == "/search.json":
            return {"docs": AUTHOR_DOCS}
        raise AssertionError(f"неожиданный путь запроса: {path}")

    monkeypatch.setattr(main, "_fetch_json", fake_fetch_json)
    return calls


@pytest.fixture
def broken_open_library(monkeypatch):
    """Эмулирует недоступность внешнего API."""

    async def fake_fetch_json(path, params=None):
        raise httpx.ConnectError("Open Library недоступен")

    monkeypatch.setattr(main, "_fetch_json", fake_fetch_json)
