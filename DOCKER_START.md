# 🐳 Запуск Standards Platform на Docker

## 📋 Быстрый старт (одна команда!)

```bash
docker compose up -d --build
```

Подожди 3-5 минут пока соберутся все контейнеры, затем:
- **Frontend**: http://localhost:80
- **Backend API**: http://localhost:5000
- **AI Chat API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Qdrant**: localhost:6333

---

## 🔧 Пошаговая инструкция

### 1️⃣ Проверь .env файл

В корне проекта должен быть файл `.env` с настройками:

```bash
cat .env
```

**Важные параметры**:
- `DB_PASSWORD` - пароль PostgreSQL
- `DEEPSEEK_API_KEY` - API ключ DeepSeek (уже настроен: sk-20296...)
- `EMBED_BACKEND=local` - использовать локальные embeddings
- `WASABI_ACCESS_KEY_ID` и `WASABI_SECRET_ACCESS_KEY` - для загрузки документов из S3

### 2️⃣ Запусти Docker Compose

```bash
# Перейди в корень проекта
cd /home/user/building-standard-website

# Запусти все сервисы (сборка + старт)
docker compose up -d --build
```

**Что происходит**:
1. Собирается **5 образов**: postgres, qdrant, backend, ai-backend, frontend
2. Создаются **3 сети** и **4 volume**
3. Запускаются все контейнеры

### 3️⃣ Проверь статус

```bash
# Посмотри запущенные контейнеры
docker compose ps

# Логи всех сервисов
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f backend
docker compose logs -f ai-backend
```

**Ожидаемый вывод**:
```
NAME                          STATUS
standards-postgres            Up (healthy)
standards-qdrant              Up (healthy)
standards-backend             Up
standards-ai-backend          Up
standards-frontend            Up
```

### 4️⃣ Инициализация баз данных

**Backend (Flask)**:
```bash
# Войди в контейнер backend
docker compose exec backend bash

# Создай таблицы и админа
python seed.py

# Выход
exit
```

**AI Backend (Django)** - уже мигрирован автоматически при старте.

### 5️⃣ Проверь работу

**Backend API**:
```bash
curl http://localhost:5000/api/health
# {"status": "OK"}
```

**AI Chat API**:
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет, как дела?"}'
```

**Frontend**:
Открой браузер → http://localhost

---

## 📁 Загрузка документов

### Вариант 1: Из Wasabi S3 (автоматически)

При запуске `seed.py` документы загрузятся из Wasabi автоматически, если настроены ключи в `.env`.

### Вариант 2: Массовая загрузка из папки

```bash
# Войди в backend контейнер
docker compose exec backend bash

# Загрузи документы из локальной папки
python scripts/bulk_upload.py /path/to/documents --no-ai

# Или с синхронизацией в AI backend
python scripts/bulk_upload.py /path/to/documents
```

### Вариант 3: Один документ через API

```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "title=SHNQ 3.01.02-23" \
  -F "category=Строительство"
```

---

## 🤖 Настройка AI Chat

### Создать тестовый документ в AI backend

```bash
docker compose exec ai-backend python manage.py shell <<EOF
from app_shnq.models import Document, Clause, Category

category, _ = Category.objects.get_or_create(
    code="SHNQ",
    defaults={"name": "Строительные нормы"}
)

doc = Document.objects.create(
    category=category,
    code="SHNQ 3.01.02-23",
    title="Жилые здания",
    lex_url="https://lex.uz/docs/test"
)

Clause.objects.create(
    document=doc,
    clause_number="5.1",
    text="Балконы должны иметь ограждение высотой не менее 1,2 метра."
)

print(f"✅ Создан документ {doc.code}")
EOF
```

### Создать embeddings

```bash
docker compose exec ai-backend python manage.py shell <<EOF
from app_shnq.embeddings import upsert_clause_embeddings
result = upsert_clause_embeddings()
print(f"✅ Embeddings: {result}")
EOF
```

### Тест AI Chat

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Какая высота ограждения балкона?"}' | jq .
```

---

## 🛠️ Полезные команды

### Перезапуск сервисов

```bash
# Перезапустить все
docker compose restart

# Перезапустить один сервис
docker compose restart backend
docker compose restart ai-backend
```

### Пересборка после изменений кода

```bash
# Пересобрать и перезапустить
docker compose up -d --build

# Только один сервис
docker compose up -d --build backend
```

### Просмотр логов

```bash
# Все сервисы (follow mode)
docker compose logs -f

# Последние 100 строк backend
docker compose logs --tail=100 backend

# Только ошибки
docker compose logs | grep -i error
```

### Очистка

```bash
# Остановить все
docker compose down

# Остановить + удалить volumes (БД будет очищена!)
docker compose down -v

# Полная очистка (осторожно!)
docker compose down -v --rmi all
```

### Войти в контейнер

```bash
# Backend
docker compose exec backend bash

# AI Backend
docker compose exec ai-backend bash

# PostgreSQL
docker compose exec postgres psql -U postgres
```

---

## 🔍 Troubleshooting

### Контейнер не стартует

```bash
# Смотри логи
docker compose logs <service-name>

# Проверь healthcheck
docker compose ps
```

### Ошибка "port already in use"

```bash
# Найди процесс на порту
sudo lsof -i :5000
sudo lsof -i :8000
sudo lsof -i :5432

# Убей процесс или измени порты в docker-compose.yml
```

### База данных пустая

```bash
# Проверь что seed.py отработал
docker compose exec backend python seed.py

# Проверь Django миграции
docker compose exec ai-backend python manage.py migrate
```

### AI Chat не находит документы

```bash
# Проверь embeddings
docker compose exec ai-backend python manage.py shell <<EOF
from app_shnq.models import ClauseEmbedding
print(f"Embeddings: {ClauseEmbedding.objects.count()}")
EOF

# Пересоздай embeddings
docker compose exec ai-backend python manage.py shell <<EOF
from app_shnq.models import ClauseEmbedding
from app_shnq.embeddings import upsert_clause_embeddings
ClauseEmbedding.objects.all().delete()
result = upsert_clause_embeddings()
print(result)
EOF
```

### Frontend показывает ошибку подключения

```bash
# Проверь что backend работает
curl http://localhost:5000/api/health

# Проверь CORS настройки в backend/app/config.py
```

---

## ✅ Проверка что все работает

1. **Frontend**: http://localhost → видна главная страница
2. **Login**: http://localhost/login → вход работает (admin@standards.uz / admin123)
3. **Backend API**: `curl http://localhost:5000/api/documents` → список документов
4. **AI Chat**: На главной странице задай вопрос в AI помощнике
5. **PostgreSQL**: `docker compose exec postgres psql -U postgres -d standards_db -c "SELECT COUNT(*) FROM documents;"`

---

## 📊 Что дальше?

1. **Загрузи 154 документа** через `bulk_upload.py` или Wasabi sync
2. **Синхронизируй** их в AI backend через `/api/sync-document/`
3. **Создай embeddings** для всех документов
4. **Доработай frontend** чтобы показывать цену и кнопку "Купить"
5. **Настрой HTTPS** для production (nginx + Let's Encrypt)

---

**Создано**: 2026-05-03  
**Версия**: 2.1.0  
**AI Backend**: PostgreSQL + Local Embeddings ✓  
**RAG**: Working ✓
