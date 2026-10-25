from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import requests
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

load_dotenv()

# Основная страница
@app.get("/")
async def home(request: Request):
    response = requests.get("https://openlibrary.org/subjects/fiction.json?limit=5")
    popular_books_data = response.json().get("works", [])
    popular_books = [
        {
            "title": book.get("title"),
            "author": book.get("authors", [{}])[0].get("name") if book.get("authors") else None,
            "cover_id": book.get("cover_id"),
            "description": book.get("description") if isinstance(book.get("description"), str) else ""
        }
        for book in popular_books_data
    ]
    return templates.TemplateResponse(request=request, name="home.html", context={"popular_books": popular_books})

# Отправка предпочтений пользователя и отображение рекомендаций
@app.post("/recommendations/")
async def recommendations(request: Request, author: str = Form(...), genre: str = Form(...)):
    genre_books_data = requests.get(f"https://openlibrary.org/subjects/{genre.lower()}.json?limit=10").json().get("works", [])
    author_books_data = requests.get(f"https://openlibrary.org/search.json?author={author}&limit=10").json().get("docs", [])

    # Извлекаем данные для книг жанра и автора, добавляя обложку и описание
    genre_books = [
        {
            "title": book.get("title"),
            "author": book.get("authors", [{}])[0].get("name"),
            "cover_id": book.get("cover_id"),
            "description": book.get("description") if isinstance(book.get("description"), str) else ""
        }
        for book in genre_books_data
    ]
    author_books = [
        {
            "title": book.get("title"),
            "author": book.get("author_name", [None])[0] if book.get("author_name") else None,
            "cover_id": book.get("cover_i"),
            "description": (
                book.get("first_sentence", [None])[0] if isinstance(book.get("first_sentence"), list)
                else book.get("first_sentence", {}).get("value", "")
            )
        }
        for book in author_books_data
    ]

    # Рекомендуемые книги (книги жанра, не попадающие в список книг по автору)
    recommendations = [book for book in genre_books if book["title"] not in [ab["title"] for ab in author_books]]
    print(recommendations)
    return templates.TemplateResponse(
        request=request,
        name="recommendations.html",
        context={
            "author_books": author_books,
            "genre_books": genre_books,
            "recommendations": recommendations,
        },
    )

# Для запуска проекта нужно прописать в терминал: docker run -p 80:80 my-fastapi-app
# Добавить изменения: docker build -t my-fastapi-app .