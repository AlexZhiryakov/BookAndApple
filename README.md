# 📚 BookAndApple — поиск и рекомендации книг

Веб-приложение на FastAPI, которое подбирает книги по любимому автору и жанру
на данных открытого API Open Library.

![CI](https://github.com/AlexZhiryakov/BookAndApple/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)

## 🔗 Живое демо

<!-- заменить: подставьте реальный адрес после деплоя на Render/Layero -->
- Сайт: [bookandapple-main.layero.app](https://bookandapple-main.layero.app)

## 📖 О проекте

Небольшое демо-приложение: главная страница показывает блок «Популярные книги»
(данные из Open Library), а форма «любимый автор + любимый жанр» строит три
списка — книги автора, книги жанра и рекомендации (книги жанра, которых нет у
автора). Обложки и описания тоже берутся из Open Library.

Проект показывает работу с асинхронным HTTP-клиентом `httpx`, кешированием
ответов внешнего API, серверным рендерингом Jinja2 и обработкой сбоев внешнего
сервиса без падения приложения.

## 🛠 Стек технологий

- **Python 3.11** — язык проекта.
- **FastAPI** — веб-фреймворк: маршруты, валидация форм, рендеринг шаблонов.
- **Uvicorn** — ASGI-сервер для запуска приложения.
- **Jinja2** — серверные HTML-шаблоны (`base.html`, `home.html`, `recommendations.html`).
- **httpx (AsyncClient)** — асинхронные запросы к Open Library с таймаутом и проверкой статуса.
- **python-dotenv** — конфигурация через переменные окружения.
- **pytest + TestClient** — тесты страниц с мок-заменителем Open Library.
- **ruff** — линтер и сортировка импортов.
- **GitHub Actions** — CI: линт и тесты на каждый push.
- **Open Library API** — источник данных о книгах и обложках.

## 🚀 Как пользоваться сайтом

1. Откройте [живое демо](https://bookandapple-main.layero.app).
2. На главной странице вы увидите блок **«Популярные книги»** (данные подгружаются автоматически).
3. Чтобы получить рекомендации:
   - Введите имя любимого автора (например, `Jane Austen` или `Tolkien`).
   - Введите интересующий жанр (например, `fantasy`, `romance` или `science fiction`).
   - Нажмите кнопку **«Найти книги»**.
4. Приложение найдёт книги этого автора, книги в выбранном жанре, а затем
   сформирует список рекомендаций, исключив дубликаты.
5. Если Open Library недоступен, вместо ошибки 500 откроется страница-заглушка
   с предложением повторить запрос позже.

## ▶️ Быстрый старт

### Локально

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r app/requirements.txt
Copy-Item .env.example .env       # при необходимости отредактируйте
uvicorn app.main:app --reload     # http://127.0.0.1:8000
```

Приложение читает шаблоны и статику по путям, построенным от
`Path(__file__).resolve().parent`, поэтому запускать можно как из корня
репозитория (`uvicorn app.main:app`), так и из каталога `app/`.

### Деплой

- `vercel.json` — сборка serverless-функции из `app/main.py`.
- `app/layero.json` — запуск `uvicorn main:app` на Layero.

Так как CSS теперь встроен прямо в `base.html`, внешний вид страниц не зависит
от того, отдаёт ли хостинг каталог `static`.

## 🧪 Тесты и качество

- `pytest` — тесты страниц и обработки ошибок; HTTP-запросы к Open Library
  подменяются моком, реальная сеть не нужна.
- `ruff check .` — линтер и проверка порядка импортов.
- CI в GitHub Actions: на каждый push и pull request запускаются линт и тесты.

```powershell
pip install -r requirements-dev.txt
ruff check .
pytest
```

## ⚙️ Переменные окружения

| Переменная               | Назначение                                  | По умолчанию            |
|--------------------------|---------------------------------------------|-------------------------|
| `OPEN_LIBRARY_BASE_URL`  | базовый адрес Open Library API              | `https://openlibrary.org` |
| `OPEN_LIBRARY_TIMEOUT`   | таймаут запросов к внешнему API (сек)       | `5`                     |
| `POPULAR_CACHE_TTL`      | время жизни кеша «популярных книг» (сек)    | `600` (10 минут)        |
| `POPULAR_LIMIT`          | сколько популярных книг запрашивать         | `12`                    |

## 📁 Структура проекта

```
BookAndApple/
├── app/
│   ├── main.py                 # FastAPI, маршруты, httpx-клиент, кеш
│   ├── requirements.txt        # зависимости приложения
│   ├── layero.json             # конфиг запуска на Layero
│   ├── static/
│   │   └── no-cover.svg        # fallback-картинка обложки
│   └── templates/
│       ├── base.html           # каркас, встроенный CSS (адаптивная вёрстка)
│       ├── _macros.html        # макрос карточки книги
│       ├── home.html           # главная: форма поиска + популярные книги
│       ├── recommendations.html# три подборки: автор / жанр / рекомендации
│       └── error.html          # страница-заглушка при сбое внешнего API
├── tests/
│   ├── conftest.py             # TestClient и мок Open Library
│   └── test_app.py             # тесты страниц и обработки ошибок
├── .github/workflows/ci.yml
├── vercel.json                 # конфиг деплоя на Vercel
├── pyproject.toml              # настройки ruff и pytest
├── requirements-dev.txt
├── .env.example
└── README.md
```

## 🧭 Что можно улучшить дальше

- Кешировать ответы по автору и жанру, а не только «популярные книги».
- Добавить пагинацию и сортировку в подборках.
- Выбрать одну платформу деплоя и убрать дублирующий конфиг
  (`vercel.json` и `app/layero.json`).
- Покрыть тестами разбор данных Open Library и добавить `pytest-cov`.
- Добавить лицензию и скриншот страницы в README.

