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
| **Vercel** | serverless-деплой |

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

## Деплой на Vercel

Проект рассчитан на **Vercel Serverless Functions** (`@vercel/python`). Конфигурация лежит в корне: `vercel.json`.

1. Установите [Vercel CLI](https://vercel.com/docs/cli):

   ```bash
   npm i -g vercel
   ```

2. Перейдите в папку проекта:

   ```bash
   cd BookAndApple
   ```

3. Запустите деплой:

   ```bash
   vercel
   ```

CLI запросит вход в аккаунт Vercel (если ещё не авторизованы) и настройки проекта. После завершения появится URL превью. Для продакшена используйте `vercel --prod`.

## Структура проекта

```text
BookAndApple/
├── app/
│   ├── main.py              # маршруты FastAPI и запросы к Open Library
│   ├── static/style.css
│   └── templates/           # Jinja2: base, home, recommendations
├── vercel.json              # маршрутизация для Vercel
├── requirements.txt
└── README.md
```

## Лицензия и данные

Каталог книг предоставляется Open Library. При публикации сервиса соблюдайте [условия использования Open Library](https://openlibrary.org/developers/api).
