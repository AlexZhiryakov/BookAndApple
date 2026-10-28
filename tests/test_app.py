"""Тесты страниц приложения: главная, рекомендации, кеш, обработка ошибок."""


def test_home_renders_popular_books(client, mock_open_library):
    response = client.get("/")
    assert response.status_code == 200
    assert "Популярные книги" in response.text
    assert "The Great Gatsby" in response.text
    assert "F. Scott Fitzgerald" in response.text


def test_home_caches_popular_books(client, mock_open_library):
    client.get("/")
    client.get("/")
    # Внешний API должен быть опрошен ровно один раз за счёт кеша.
    assert mock_open_library["count"] == 1


def test_home_shows_stub_when_api_fails(client, broken_open_library):
    response = client.get("/")
    assert response.status_code == 200
    assert "Сервис временно недоступен" in response.text


def test_home_uses_fallback_cover(client, mock_open_library):
    response = client.get("/")
    # У книги «No Cover Book» нет cover_id — должна подставляться заглушка.
    assert "no-cover.svg" in response.text


def test_static_fallback_image_is_served(client):
    response = client.get("/static/no-cover.svg")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg")


def test_recommendations_lists_author_genre_and_suggestions(client, mock_open_library):
    response = client.post("/recommendations/", data={"author": "F. Scott Fitzgerald", "genre": "fiction"})
    assert response.status_code == 200
    assert "Книги автора «F. Scott Fitzgerald»" in response.text
    assert "Книги в жанре «fiction»" in response.text
    assert "Рекомендуем ещё" in response.text
    # «No Cover Book» есть в жанре, но не у автора — попадает в рекомендации.
    assert "No Cover Book" in response.text


def test_recommendations_shows_stub_when_api_fails(client, broken_open_library):
    response = client.post("/recommendations/", data={"author": "Anyone", "genre": "fiction"})
    assert response.status_code == 200
    assert "Сервис временно недоступен" in response.text


def test_recommendations_rejects_empty_author(client, mock_open_library):
    response = client.post("/recommendations/", data={"author": "", "genre": "fiction"})
    assert response.status_code == 422
