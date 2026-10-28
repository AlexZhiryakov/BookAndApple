"""BookAndApple — поиск и рекомендации книг на FastAPI и Open Library."""

from __future__ import annotations

import os
import time
from pathlib import Path
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Пути строим от файла, чтобы приложение работало из любого рабочего каталога
# и не зависело от схемы деплоя.
BASE_DIR = Path(__file__).resolve().parent

load_dotenv()

OPEN_LIBRARY_BASE_URL = os.getenv("OPEN_LIBRARY_BASE_URL", "https://openlibrary.org").rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("OPEN_LIBRARY_TIMEOUT", "5"))
POPULAR_CACHE_TTL = float(os.getenv("POPULAR_CACHE_TTL", "600"))
POPULAR_LIMIT = int(os.getenv("POPULAR_LIMIT", "12"))

app = FastAPI(title="BookAndApple", description="Поиск и рекомендации книг по данным Open Library")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Кеш «популярных книг»: (время записи по monotonic, список книг).
_popular_cache: tuple[float, list[dict]] | None = None


async def _fetch_json(path: str, params: dict | None = None) -> dict:
    """GET-запрос к Open Library с таймаутом и проверкой статуса ответа.

    Бросает ``httpx.HTTPError`` при сетевой ошибке, таймауте или статусе >= 400
    и ``ValueError`` при некорректном JSON.
    """
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.get(f"{OPEN_LIBRARY_BASE_URL}{path}", params=params)
        response.raise_for_status()
        return response.json()


def _work_to_book(work: dict) -> dict:
    """Приводит работу из эндпоинта ``/subjects/*.json`` к общему виду."""
    authors = work.get("authors") or []
    author = authors[0].get("name") if authors and isinstance(authors[0], dict) else None
    description = work.get("description")
    return {
        "title": work.get("title") or "Без названия",
        "author": author,
        "cover_id": work.get("cover_id"),
        "description": description if isinstance(description, str) else "",
    }


def _doc_to_book(doc: dict) -> dict:
    """Приводит документ из эндпоинта ``/search.json`` к общему виду."""
    author_names = doc.get("author_name") or []
    first_sentence = doc.get("first_sentence")
    if isinstance(first_sentence, list):
        description = first_sentence[0] if first_sentence else ""
    elif isinstance(first_sentence, dict):
        description = first_sentence.get("value", "")
    else:
        description = ""
    return {
        "title": doc.get("title") or "Без названия",
        "author": author_names[0] if author_names else None,
        "cover_id": doc.get("cover_i"),
        "description": description or "",
    }


async def _get_popular_books() -> list[dict]:
    """Возвращает популярные книги, кешируя результат на ``POPULAR_CACHE_TTL`` секунд."""
    global _popular_cache
    now = time.monotonic()
    if _popular_cache is not None and now - _popular_cache[0] < POPULAR_CACHE_TTL:
        return _popular_cache[1]
    data = await _fetch_json("/subjects/fiction.json", {"limit": POPULAR_LIMIT})
    books = [_work_to_book(work) for work in data.get("works", [])]
    _popular_cache = (now, books)
    return books


def _error_page(request: Request, message: str, **extra: object):
    """Страница-заглушка вместо 500 при недоступности внешнего API."""
    context = {"message": message, **extra}
    return templates.TemplateResponse(request=request, name="error.html", context=context)


@app.get("/")
async def home(request: Request):
    """Главная страница с формой поиска и блоком популярных книг."""
    try:
        popular_books = await _get_popular_books()
    except (httpx.HTTPError, ValueError):
        return _error_page(
            request,
            "Не удалось загрузить популярные книги: сервис Open Library временно недоступен. "
            "Попробуйте обновить страницу позже.",
        )
    return templates.TemplateResponse(request=request, name="home.html", context={"popular_books": popular_books})


@app.post("/recommendations/")
async def recommendations(
    request: Request,
    author: str = Form(..., min_length=1, max_length=80),
    genre: str = Form(..., min_length=1, max_length=60),
):
    """Строит три списка: книги автора, книги жанра и рекомендации."""
    author = author.strip()
    genre = genre.strip()
    try:
        genre_data = await _fetch_json(f"/subjects/{quote(genre.lower())}.json", {"limit": 10})
        author_data = await _fetch_json("/search.json", {"author": author, "limit": 10})
    except (httpx.HTTPError, ValueError):
        return _error_page(
            request,
            "Не удалось получить данные из Open Library: сервис временно недоступен. "
            "Попробуйте ещё раз чуть позже.",
            author=author,
            genre=genre,
        )

    genre_books = [_work_to_book(work) for work in genre_data.get("works", [])]
    author_books = [_doc_to_book(doc) for doc in author_data.get("docs", [])]
    author_titles = {book["title"] for book in author_books}
    recommendations = [book for book in genre_books if book["title"] not in author_titles]

    return templates.TemplateResponse(
        request=request,
        name="recommendations.html",
        context={
            "author": author,
            "genre": genre,
            "author_books": author_books,
            "genre_books": genre_books,
            "recommendations": recommendations,
        },
    )
