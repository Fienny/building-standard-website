# Django AI Backend Dockerfile
FROM python:3.14-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    django \
    djangorestframework \
    django-cors-headers \
    openai \
    python-dotenv \
    django-jazzmin \
    requests \
    psycopg2-binary \
    dj-database-url \
    qdrant-client \
    sentence-transformers

# Копируем код приложения
COPY . .

# Порт Django
EXPOSE 8000

# Миграции и запуск
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
