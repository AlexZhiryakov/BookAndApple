# BookAndApple

Веб-приложение на **FastAPI** для поиска и рекомендации книг. Пользователь указывает любимого автора и жанр — сервис показывает подборку книг автора, книги жанра и персональные рекомендации.

Данные о книгах и обложках загружаются из внешнего API **[Open Library](https://openlibrary.org/developers/api)** — собственная база данных не используется.

## Стек

| Технология | Роль |
| --- | --- |
| **Python** | язык приложения |
| **FastAPI** | веб-фреймворк и маршруты |
| **Uvicorn** | ASGI-сервер |
| **Jinja2** | HTML-шаблоны |
| **Docker** | контейнеризация и деплой |

## Возможности

- Главная страница с популярными книгами (предмет `fiction` в Open Library)
- Поиск по автору (`/search.json`) и по жанру (`/subjects/{genre}.json`)
- Рекомендации: книги выбранного жанра без пересечения с книгами автора
- Обложки с `covers.openlibrary.org`
- Интерактивная документация API: [`/docs`](http://localhost:8000/docs) (Swagger) и [`/redoc`](http://localhost:8000/redoc)

## Маршруты

| Метод | Путь | Описание |
| --- | --- | --- |
| `GET` | `/` | Главная страница и форма поиска |
| `POST` | `/recommendations/` | Подборка книг и рекомендации по автору и жанру |
| `GET` | `/static/...` | Статические файлы (CSS) |

## Запуск через Docker

Нужен установленный [Docker](https://docs.docker.com/get-docker/).

Сборка образа:

```bash
docker build -t bookandapple .
```

Запуск контейнера:

```bash
docker run -p 8000:8000 -e PORT=8000 bookandapple
```

Откройте в браузере: [http://localhost:8000](http://localhost:8000).

Переменная `PORT` задаёт порт внутри контейнера (так же, как на хостинге Render). Сопоставление `-p 8000:8000` публикует этот порт на машине.

## Запуск локально

Требуются Python 3.10+ и `pip`.

1. Создайте и активируйте виртуальное окружение:

   ```bash
   python -m venv venv
   ```

   Windows (PowerShell):

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   macOS / Linux:

   ```bash
   source venv/bin/activate
   ```

2. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

3. Запустите сервер из папки `app` (шаблоны и статика подключаются относительно рабочей директории):

   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

Приложение будет доступно по адресу [http://localhost:8000](http://localhost:8000).

## Структура проекта

```text
BookAndApple/
├── app/
│   ├── main.py              # маршруты FastAPI и запросы к Open Library
│   ├── static/style.css
│   └── templates/           # Jinja2: base, home, recommendations
├── Dockerfile
├── requirements.txt
└── README.md
```

## Лицензия и данные

Каталог книг предоставляется Open Library. При публикации сервиса соблюдайте [условия использования Open Library](https://openlibrary.org/developers/api).
