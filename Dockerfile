FROM python:3.10

# Установка рабочей директории
WORKDIR /app

# Копируем requirements.txt в контейнер
COPY requirements.txt .

# Установка зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копия папки app в контейнер
COPY ./app /app

COPY ./app/templates /app/templates
COPY ./app/static /app/static

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]