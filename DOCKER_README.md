# 🐳 Docker Setup для Standards Platform

Весь стек в одной команде: Flask Backend + Django AI + PostgreSQL + Qdrant + Frontend

## 📋 Предварительные требования

1. **Docker** и **Docker Compose** установлены
2. **DeepSeek API ключ** (бесплатный):
   - Зарегистрируйтесь на https://platform.deepseek.com/
   - Создайте API ключ
   - Вставьте в `.env` файл

## 🚀 Быстрый старт

### 1. Настройка переменных окружения

```bash
# .env файл уже создан, нужно только добавить DeepSeek API ключ
nano .env  # или любой редактор

# Найдите строку:
DEEPSEEK_API_KEY=sk-YOUR-DEEPSEEK-API-KEY-HERE

# И замените на ваш ключ:
DEEPSEEK_API_KEY=sk-ваш-настоящий-ключ
```

### 2. Запуск всего стека

```bash
# Соберите и запустите все сервисы
docker-compose up --build

# Или в фоновом режиме:
docker-compose up -d --build
```

### 3. Проверка работы

После запуска откройте:

- **Frontend**: http://localhost (порт 80)
- **Flask Backend API**: http://localhost:5000
- **Django AI Backend**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Qdrant**: http://localhost:6333

### 4. Загрузка документов

```bash
# Зайдите в контейнер backend
docker exec -it standards-backend bash

# Запустите bulk upload
python /app/scripts/bulk_upload.py /path/to/documents --no-ai

# Или с AI синхронизацией (после настройки DeepSeek)
python /app/scripts/bulk_upload.py /path/to/documents
```

## 📦 Сервисы в составе

| Сервис | Порт | Описание |
|--------|------|----------|
| `frontend` | 80 | React приложение (Nginx) |
| `backend` | 5000 | Flask REST API |
| `ai-backend` | 8000 | Django AI для умного поиска |
| `postgres` | 5432 | PostgreSQL (2 БД: standards_db, standards_ai_db) |
| `qdrant` | 6333 | Векторная БД для embeddings |

## 🛠️ Полезные команды

```bash
# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f ai-backend

# Остановка
docker-compose down

# Остановка с удалением volumes (ОСТОРОЖНО! Удалит все данные)
docker-compose down -v

# Перезапуск одного сервиса
docker-compose restart backend

# Пересборка после изменений в коде
docker-compose up --build backend

# Войти в контейнер
docker exec -it standards-backend bash
docker exec -it standards-ai-backend bash

# Выполнить команду в контейнере
docker exec standards-backend python seed.py
```

## 🔧 Миграции базы данных

### Flask Backend
```bash
docker exec -it standards-backend python seed.py
```

### Django AI Backend
```bash
docker exec -it standards-ai-backend python manage.py makemigrations
docker exec -it standards-ai-backend python manage.py migrate
docker exec -it standards-ai-backend python manage.py createsuperuser
```

## 📊 Мониторинг

### Проверка здоровья сервисов
```bash
# Все сервисы
docker-compose ps

# Healthcheck
docker inspect --format='{{.State.Health.Status}}' standards-backend
docker inspect --format='{{.State.Health.Status}}' standards-db
```

### PostgreSQL
```bash
# Подключиться к БД
docker exec -it standards-db psql -U standards_user -d standards_db

# Список таблиц
\dt

# Проверка документов
SELECT COUNT(*) FROM documents;
```

### Qdrant
```bash
# API запрос
curl http://localhost:6333/collections
```

## 🐛 Troubleshooting

### Порты заняты
```bash
# Проверьте что порты свободны
sudo lsof -i :80
sudo lsof -i :5000
sudo lsof -i :8000
sudo lsof -i :5432
sudo lsof -i :6333

# Или измените порты в docker-compose.yml
```

### Ошибки при сборке
```bash
# Очистите Docker кеш
docker system prune -a
docker volume prune

# Пересоберите с нуля
docker-compose down -v
docker-compose up --build
```

### PostgreSQL не стартует
```bash
# Удалите volume и пересоздайте
docker-compose down
docker volume rm building-standard-website_postgres-data
docker-compose up
```

### Qdrant connection refused
```bash
# Проверьте запущен ли Qdrant
docker-compose ps qdrant

# Рестартуйте
docker-compose restart qdrant
```

## 📝 Структура данных

### Volumes
- `postgres-data` - данные PostgreSQL
- `qdrant-data` - векторные embeddings
- `backend-uploads` - временные загрузки (основные файлы на Wasabi)
- `ai-media` - медиа файлы Django

### Networks
- `standards-network` - внутренняя сеть для всех сервисов

## 🚢 Production Deployment

Для продакшена рекомендуется:

1. Использовать `.env.production` с безопасными паролями
2. Настроить Nginx reverse proxy
3. Включить HTTPS (Let's Encrypt)
4. Настроить backup для PostgreSQL и Qdrant
5. Использовать Docker Swarm или Kubernetes для масштабирования

## 📚 Дополнительно

- Flask Backend: `./backend/README.md`
- Django AI Backend: `./AI-ready-project/shnq_ai_backend/README.md`
- Frontend: `./frontend/README.md`

---

**Готово!** Теперь весь стек запускается одной командой `docker-compose up` 🎉
