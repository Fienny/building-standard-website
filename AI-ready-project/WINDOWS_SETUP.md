# Запуск AI-помощника на Windows

## Требования

- Python 3.12+ (рекомендуется 3.14)
- DeepSeek API ключ (https://platform.deepseek.com/)

## Быстрый запуск

### 1. Установка зависимостей

```powershell
cd AI-ready-project\shnq_ai_backend

# Создайте виртуальное окружение
python -m venv venv

# Активируйте
.\venv\Scripts\Activate.ps1

# Установите зависимости
pip install django djangorestframework django-cors-headers django-jazzmin openai python-dotenv qdrant-client sentence-transformers
```

### 2. Настройка переменных окружения

Создайте файл `.env` в папке `AI-ready-project/shnq_ai_backend/`:

```env
# DeepSeek API (обязательно)
DEEPSEEK_API_KEY=ваш_api_ключ_от_deepseek
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_CHAT_MODEL=deepseek-chat
DEEPSEEK_EMBED_MODEL=deepseek-embedding

# Опциональные настройки
DEEPSEEK_EMBED_FALLBACK=hash
DEEPSEEK_CHAT_TIMEOUT=45
DEEPSEEK_EMBED_TIMEOUT=12
RAG_REWRITE_QUERY=0
RAG_RERANK_ENABLED=0
RAG_EMBED_CACHE=1
```

**Где получить DeepSeek API ключ:**
1. Зарегистрируйтесь на https://platform.deepseek.com/
2. Пополните баланс ($5-10 хватит надолго)
3. Создайте API ключ в разделе API Keys

### 3. Инициализация базы данных

```powershell
# Применить миграции (создаст SQLite базу)
python manage.py migrate

# (Опционально) Создать суперпользователя для админки
python manage.py createsuperuser
```

### 4. Запуск сервера

```powershell
# Запустить Django dev-сервер
python manage.py runserver

# Сервер запустится на http://localhost:8000
```

## Проверка работы

### Админ-панель
Откройте http://localhost:8000/admin/

Здесь можно загружать документы и управлять данными.

### API проверка

```powershell
# Отправьте тестовый запрос
Invoke-WebRequest -Uri http://localhost:8000/api/chat/ `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"message":"Salom"}'
```

Если все работает, получите ответ с приветствием.

## Добавление документов

1. Откройте админку http://localhost:8000/admin/
2. Зайдите в "Documents"
3. Создайте категорию (SHNQ, QMQ, SanQvaN)
4. Загрузите документ (DOC/DOCX файл)
5. Система автоматически извлечет текст и создаст эмбеддинги

## Интеграция с основным проектом

AI backend автоматически доступен для Flask backend через прокси `/api/ai/chat`.

Убедитесь, что в `backend/.env` указано:
```env
AI_BACKEND_URL=http://localhost:8000
```

## Troubleshooting

### Ошибка "DeepSeek API key not found"
- Проверьте, что файл `.env` создан в правильной папке
- Убедитесь, что `DEEPSEEK_API_KEY` указан корректно

### Ошибка при установке зависимостей
```powershell
# Обновите pip
python -m pip install --upgrade pip

# Попробуйте установить по одной
pip install django
pip install djangorestframework
# и т.д.
```

### База данных не создается
```powershell
# Удалите старую БД и пересоздайте
del db.sqlite3
python manage.py migrate
```

## Дополнительно

### Загрузка эмбеддингов из DOC файлов

Если у вас есть DOC/DOCX файлы стандартов в папке `docs/original/`:

```powershell
# Запустить обработку
python shnq_embding_llmma.py --force
```

Это извлечёт текст, создаст эмбеддинги и загрузит в БД.

### Использование без DeepSeek

Если нет ключа DeepSeek, можно использовать fallback на sentence-transformers:

```env
DEEPSEEK_EMBED_FALLBACK=sentence-transformers
```

Но качество ответов будет хуже.

---

**Готово!** AI-помощник работает на http://localhost:8000
