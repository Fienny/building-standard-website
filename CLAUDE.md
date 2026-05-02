# Standards Platform - Документация для AI-ассистента

## О проекте

**Платформа для продажи государственных строительных стандартов Республики Узбекистан**, переведенных на русский язык.

**Бизнес-модель**: Freemium - пользователи могут бесплатно просмотреть первые 2 страницы любого документа, полный доступ после оплаты (1 страница = 1000 сум).

---

## Архитектура системы

### Основной стек

```
┌─────────────────────────────────────────────────┐
│           Standards Platform Stack              │
├─────────────────────────────────────────────────┤
│                                                 │
│  Frontend (React 19 + Vite 7)                   │
│    ├── Port: 5173 (dev) / 80 (prod)            │
│    ├── Router: React Router 7                   │
│    └── State: Context API + JWT                 │
│                                                 │
│  Backend (Flask 3.1 + Python 3.12+)             │
│    ├── Port: 5000                               │
│    ├── Auth: flask-jwt-extended                 │
│    ├── ORM: Flask-SQLAlchemy 3.1                │
│    ├── PDF: PyMuPDF (превью первых 2 страниц)  │
│    ├── Storage: Wasabi S3 (eu-central-1)       │
│    └── Payments: Click, PayMe, Uzcard/Humo     │
│                                                 │
│  AI Backend (Django 6.0 + DeepSeek)             │
│    ├── Port: 8000                               │
│    ├── AI: DeepSeek API (RAG система)          │
│    ├── Embeddings: Sentence-Transformers       │
│    └── Vector DB: Qdrant                        │
│                                                 │
│  Database (PostgreSQL 15)                       │
│    ├── Port: 5432                               │
│    ├── standards_db - основная БД Flask        │
│    └── standards_ai_db - БД для Django AI      │
│                                                 │
│  Vector Database (Qdrant)                       │
│    ├── Port: 6333 (API), 6334 (gRPC)          │
│    └── Storage: Векторные embeddings            │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Deployment архитектура

**Production**:
- **Server**: DigitalOcean Droplet
- **Storage**: QNAP NAS TS-433 (NFS mount) + Wasabi S3 Cloud
- **Web Server**: Nginx (reverse proxy)
- **SSL**: Let's Encrypt
- **Deploy**: Docker Compose

---

## Структура проекта

```
building-standard-website/
│
├── frontend/                          # React SPA
│   ├── src/
│   │   ├── components/
│   │   │   └── Navigation.jsx         # Навигация
│   │   ├── pages/
│   │   │   ├── Home.jsx               # Главная + AI-помощник
│   │   │   ├── Documents.jsx          # Каталог документов
│   │   │   ├── DocumentPreview.jsx    # Превью + покупка
│   │   │   ├── Login.jsx              # Вход
│   │   │   └── Signup.jsx             # Регистрация
│   │   ├── utils/
│   │   │   ├── api.js                 # HTTP-клиент с JWT
│   │   │   └── AuthContext.jsx        # Контекст авторизации
│   │   ├── App.jsx                    # Главный роутинг
│   │   └── main.jsx                   # Точка входа
│   ├── vite.config.js                 # Dev proxy /api → :5000
│   ├── Dockerfile                     # Production build (Nginx)
│   └── package.json
│
├── backend/                           # Flask REST API
│   ├── app/
│   │   ├── __init__.py                # App factory
│   │   ├── config.py                  # Конфигурация
│   │   ├── models/
│   │   │   ├── user.py                # User model
│   │   │   ├── document.py            # Document model
│   │   │   ├── purchase.py            # Purchase model
│   │   │   └── payment.py             # Payment model
│   │   ├── routes/
│   │   │   ├── auth.py                # /api/auth/*
│   │   │   ├── documents.py           # /api/documents/*
│   │   │   ├── payments.py            # /api/payments/*
│   │   │   └── users.py               # /api/users/*
│   │   └── services/
│   │       ├── file_service.py        # PDF-превью (PyMuPDF)
│   │       ├── wasabi_service.py      # Wasabi S3 интеграция
│   │       ├── click_service.py       # Click платежи
│   │       ├── payme_service.py       # PayMe (JSON-RPC)
│   │       └── card_service.py        # Uzcard/Humo
│   ├── scripts/
│   │   └── bulk_upload.py             # Массовая загрузка документов
│   ├── run.py                         # Dev-сервер
│   ├── wsgi.py                        # Gunicorn entry point
│   ├── seed.py                        # Инициализация БД + тестовые данные
│   ├── Dockerfile
│   ├── requirements.txt               # Linux dependencies
│   ├── requirements-windows.txt       # Windows dependencies
│   └── .env.example
│
├── AI-ready-project/
│   └── shnq_ai_backend/               # Django AI Backend
│       ├── ai_assistant/              # AI app
│       │   ├── models.py              # Document, Question, Answer
│       │   ├── views.py               # /chat endpoint
│       │   └── ai_service.py          # DeepSeek + RAG
│       ├── shnq_ai_backend/
│       │   ├── settings.py            # Django settings
│       │   └── urls.py
│       ├── manage.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── docker-compose.yml                 # Полный стек (5 сервисов)
├── init-db.sql                        # Инициализация PostgreSQL
├── .env                               # Переменные окружения для Docker
│
├── CLAUDE.md                          # Этот файл - документация для AI
├── README.md                          # Общая документация
├── DOCKER_README.md                   # Docker инструкции
├── WINDOWS_GUIDE.md                   # Подробный Windows гайд
├── DROPLET_DEPLOYMENT.md              # Production deployment
├── PAYMENT_INTEGRATION.md             # Платежные системы
├── QNAP_SETUP_GUIDE.md               # QNAP NAS настройка
└── CHANGELOG.md                       # История изменений
```

---

## База данных

### PostgreSQL схема (standards_db)

**Таблицы**:

1. **users** - Пользователи
   - `id` (PK, Integer)
   - `email` (String, unique)
   - `password_hash` (String)
   - `first_name`, `last_name` (String)
   - `phone` (String, nullable)
   - `is_admin` (Boolean, default=False)
   - `created_at` (DateTime)

2. **documents** - Документы (стандарты)
   - `id` (PK, Integer)
   - `code` (String, unique) - например "ОзДСт 2710:2019"
   - `title_ru` (String) - название на русском
   - `title_uz` (String, nullable) - название на узбекском
   - `category` (String) - категория
   - `page_count` (Integer) - количество страниц
   - `year` (Integer, nullable) - год издания
   - `language` (String) - язык документа
   - `file_path` (String) - путь к файлу
   - `wasabi_key` (String, nullable) - ключ в Wasabi S3
   - `file_size` (Integer, nullable) - размер файла в байтах
   - `description` (Text, nullable)
   - `created_at` (DateTime)
   - `updated_at` (DateTime)

3. **purchases** - Покупки документов
   - `id` (PK, Integer)
   - `user_id` (FK → users.id)
   - `document_id` (FK → documents.id)
   - `price` (Float) - цена на момент покупки
   - `purchased_at` (DateTime)
   - `payment_id` (FK → payments.id, nullable)

4. **payments** - Платежи
   - `id` (PK, Integer)
   - `user_id` (FK → users.id)
   - `document_id` (FK → documents.id)
   - `amount` (Float) - сумма в сумах
   - `status` (String) - pending/success/failed/cancelled
   - `payment_method` (String) - click/payme/card
   - `transaction_id` (String, nullable) - ID транзакции платежной системы
   - `payment_url` (String, nullable) - URL для оплаты
   - `created_at` (DateTime)
   - `updated_at` (DateTime)

### PostgreSQL схема (standards_ai_db)

**Django AI Backend использует отдельную БД** для хранения:
- `ai_assistant_document` - документы для AI
- `ai_assistant_question` - история вопросов
- `ai_assistant_answer` - история ответов

---

## API Endpoints

### Аутентификация `/api/auth/*`

- `POST /api/auth/register` - Регистрация
  - Body: `{email, password, first_name, last_name, phone?}`
  - Response: `{message, access_token}`

- `POST /api/auth/login` - Вход
  - Body: `{email, password}`
  - Response: `{access_token, user: {...}}`

- `GET /api/auth/me` - Текущий пользователь (требует JWT)
  - Headers: `Authorization: Bearer <token>`
  - Response: `{id, email, first_name, last_name, is_admin, ...}`

### Документы `/api/documents/*`

- `GET /api/documents` - Список документов
  - Query params: `?search=текст&category=категория&page=1&per_page=10`
  - Response: `{documents: [...], total, page, pages, per_page}`

- `GET /api/documents/categories` - Список категорий
  - Response: `{categories: ["Общие положения", "Строительные материалы", ...]}`

- `GET /api/documents/<id>` - Детали документа
  - Response: `{id, code, title_ru, category, page_count, price, has_purchased, ...}`

- `GET /api/documents/<id>/preview` - PDF превью (первые 2 страницы)
  - Response: PDF file (Content-Type: application/pdf)

- `GET /api/documents/<id>/download` - Скачать полный документ (требует JWT + покупку)
  - Headers: `Authorization: Bearer <token>`
  - Response: PDF file или 403 если не куплен

### Платежи `/api/payments/*`

- `POST /api/payments/create` - Создать платеж
  - Body: `{document_id, payment_method: "click"|"payme"|"card"}`
  - Response: `{payment_id, payment_url, amount}`

- `GET /api/payments/status/<id>` - Статус платежа
  - Response: `{id, status, amount, document_id, ...}`

- `GET /api/payments/history` - История платежей (требует JWT)
  - Response: `{payments: [...]}`

- `POST /api/payments/callback/click` - Click webhook
- `POST /api/payments/callback/payme` - PayMe webhook (JSON-RPC 2.0)
- `POST /api/payments/callback/card` - Card webhook

### Пользователь `/api/users/*`

- `GET /api/users/profile` - Профиль (требует JWT)
  - Response: `{id, email, first_name, last_name, phone, ...}`

- `PUT /api/users/profile` - Обновить профиль
  - Body: `{first_name?, last_name?, phone?}`

- `PUT /api/users/password` - Сменить пароль
  - Body: `{old_password, new_password}`

- `GET /api/users/purchases` - Купленные документы
  - Response: `{purchases: [{document: {...}, purchased_at, price}, ...]}`

### AI Assistant `/api/ai/chat` (проксируется на Django :8000)

- `POST /api/ai/chat` - Задать вопрос AI
  - Body: `{message: "Что говорится в пункте 38 SHNQ 3.01.02-23?"}`
  - Response: `{answer, sources: [...], table_html?, image_urls?: [...], meta: {...}}`

---

## Переменные окружения

### Docker Compose (.env в корне)

```env
# PostgreSQL
DB_PASSWORD=standards_secure_pass_2024

# Flask Backend
SECRET_KEY=flask-super-secret-key-change-in-production-2024
JWT_SECRET_KEY=jwt-super-secret-key-change-in-production-2024
FRONTEND_URL=http://localhost

# Wasabi S3 Storage
WASABI_ACCESS_KEY_ID=<ваш_access_key>
WASABI_SECRET_ACCESS_KEY=<ваш_secret_key>
WASABI_BUCKET_NAME=standards
WASABI_REGION=eu-central-1

# DeepSeek AI
DEEPSEEK_API_KEY=sk-YOUR-DEEPSEEK-API-KEY-HERE
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Payment Systems (опционально)
CLICK_MERCHANT_ID=...
CLICK_SERVICE_ID=...
CLICK_SECRET_KEY=...
PAYME_MERCHANT_ID=...
PAYME_SECRET_KEY=...
```

### Backend (.env в backend/)

```env
# Flask
FLASK_ENV=production
SECRET_KEY=change-this-to-a-random-secret-key
JWT_SECRET_KEY=change-this-to-a-different-random-key

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/standards_db

# Wasabi S3
WASABI_ACCESS_KEY_ID=...
WASABI_SECRET_ACCESS_KEY=...
WASABI_BUCKET_NAME=standards
WASABI_REGION=eu-central-1

# Pricing
PRICE_PER_PAGE=1000

# Frontend URL (CORS)
FRONTEND_URL=http://localhost:5173

# AI Backend
AI_BACKEND_URL=http://localhost:8000
```

---

## Docker Services

### docker-compose.yml включает 5 сервисов:

1. **postgres** (standards-db)
   - Image: `postgres:15-alpine`
   - Port: `5432`
   - Volumes: `postgres-data`, `init-db.sql`
   - Healthcheck: `pg_isready`

2. **backend** (standards-backend)
   - Build: `./backend/Dockerfile`
   - Port: `5000`
   - Depends: postgres (healthy)
   - Volumes: `backend-uploads`
   - Env: Wasabi, DB, JWT

3. **qdrant** (standards-qdrant)
   - Image: `qdrant/qdrant:latest`
   - Ports: `6333` (API), `6334` (gRPC)
   - Volumes: `qdrant-data`
   - Healthcheck: `curl http://localhost:6333/health`

4. **ai-backend** (standards-ai-backend)
   - Build: `./AI-ready-project/shnq_ai_backend/Dockerfile`
   - Port: `8000`
   - Depends: postgres, qdrant (healthy)
   - Env: DeepSeek API, Qdrant connection

5. **frontend** (standards-frontend)
   - Build: `./frontend/Dockerfile`
   - Port: `80`
   - Nginx static serve + reverse proxy
   - Depends: backend, ai-backend

**Network**: `standards-network` (bridge)

**Volumes**:
- `postgres-data` - PostgreSQL данные
- `qdrant-data` - Векторные embeddings
- `backend-uploads` - Временные загрузки
- `ai-media` - Django media files

---

## Важные скрипты

### backend/seed.py
Инициализирует БД и создает тестовые данные:
- 1 администратор: `admin@standards.uz` / `admin123`
- 10 тестовых документов разных категорий

**Запуск**: `python seed.py`

### backend/scripts/bulk_upload.py
Массовая загрузка документов из папки:
```bash
python scripts/bulk_upload.py /path/to/documents --no-ai
```

Параметры:
- `--no-ai` - загружать без синхронизации с AI backend
- `--category` - задать категорию
- По умолчанию синхронизирует с Django AI backend

---

## Deployment сценарии

### 1. Docker (рекомендуется)

```bash
# Запуск всего стека
docker-compose up -d --build

# Проверка
docker-compose ps
docker-compose logs -f

# Остановка
docker-compose down
```

### 2. Windows без Docker

**Требования**:
- Python 3.12+
- Node.js 18+
- PostgreSQL 15+

**3 терминала**:
1. Backend: `cd backend && python run.py` (порт 5000)
2. Frontend: `cd frontend && npm run dev` (порт 5173)
3. AI Backend: `cd AI-ready-project/shnq_ai_backend && python manage.py runserver` (порт 8000)

Подробно: см. WINDOWS_GUIDE.md

### 3. Production (DigitalOcean + QNAP NFS)

См. DROPLET_DEPLOYMENT.md

---

## Платежные системы

### Click
- Протокол: HMAC-SHA1
- Webhook: `/api/payments/callback/click`
- Методы: `prepare`, `complete`

### PayMe
- Протокол: JSON-RPC 2.0
- Webhook: `/api/payments/callback/payme`
- Методы: `CheckPerformTransaction`, `CreateTransaction`, `PerformTransaction`, `CancelTransaction`, `CheckTransaction`

### Uzcard/Humo
- Протокол: HMAC-SHA256
- Webhook: `/api/payments/callback/card`
- Методы зависят от агрегатора

**Подробно**: см. PAYMENT_INTEGRATION.md

---

## AI-помощник (RAG система)

### Как работает:

1. **Документы загружаются** через `bulk_upload.py` → синхронизируются с Django AI backend
2. **Django создает embeddings** через Sentence-Transformers
3. **Embeddings сохраняются** в Qdrant vector database
4. **Пользователь задает вопрос** → Flask проксирует на Django
5. **Django выполняет RAG**:
   - Создает embedding вопроса
   - Ищет похожие фрагменты в Qdrant
   - Отправляет контекст + вопрос в DeepSeek API
   - Возвращает ответ с источниками

### DeepSeek API ключ

**Получить бесплатно**:
1. https://platform.deepseek.com/
2. Регистрация
3. API Keys → Create new key
4. Добавить в `.env`: `DEEPSEEK_API_KEY=sk-...`

---

## Troubleshooting

### Docker

**Порты заняты**:
```bash
docker-compose down
sudo lsof -i :80
sudo lsof -i :5000
# Убить процессы или изменить порты в docker-compose.yml
```

**PostgreSQL не стартует**:
```bash
docker-compose down
docker volume rm building-standard-website_postgres-data
docker-compose up -d
```

**Логи**:
```bash
docker-compose logs -f backend
docker-compose logs -f ai-backend
docker-compose logs -f frontend
```

### Windows

**Ошибка "execution policy"**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**PostgreSQL connection refused**:
- Проверить что PostgreSQL запущен в Services
- Проверить пароль в `.env`
- Создать БД: `CREATE DATABASE standards_db;`

**Frontend не запускается**:
```powershell
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## Принятые технические решения

### Почему Wasabi S3, а не QNAP NAS?

**Изначально**: Планировалось хранить файлы на QNAP NAS TS-433 в офисе с NFS mount на DigitalOcean Droplet.

**Проблема**: NFS через интернет нестабилен, медленный, зависит от интернета офиса.

**Решение**: Wasabi S3 Cloud Storage (S3-совместимый)
- Регион: `eu-central-1` (ближе к Узбекистану)
- Стоимость: $5.99/TB/месяц (без egress fees)
- Скорость: CDN-уровень
- Надежность: 11 nines (99.999999999%)

**QNAP теперь**: Используется только для локального бэкапа и временного хранения.

### Почему две PostgreSQL базы?

- **standards_db** - Flask backend (users, documents, purchases, payments)
- **standards_ai_db** - Django AI backend (ai documents, questions, answers)

**Причина**: Django требует полный контроль над миграциями, Flask использует Alembic. Разделение предотвращает конфликты.

### Почему DeepSeek, а не OpenAI/Claude?

**DeepSeek** выбран потому что:
- Бесплатный API tier (с лимитами)
- Хорошее качество для русского языка
- Поддержка длинных контекстов (до 64K tokens)
- Дешевле коммерческих API

**Альтернативы** (можно заменить в `ai_service.py`):
- OpenAI GPT-4
- Anthropic Claude
- Google Gemini
- Любая OpenAI-совместимая API

---

## Roadmap

### В разработке
- [ ] Админ-панель для управления документами
- [ ] Система скидок и промокодов
- [ ] Email-уведомления о покупках
- [ ] Мобильное приложение (React Native)

### Планируется
- [ ] Подписочная модель (monthly/yearly)
- [ ] Корпоративные аккаунты
- [ ] Экспорт документов в Word/Excel
- [ ] Multilingual support (Uzbek, English)
- [ ] API для партнеров

---

## Контакты и поддержка

**GitHub**: https://github.com/your-repo/building-standard-website

**Issues**: https://github.com/your-repo/building-standard-website/issues

**Email**: support@standards.uz (настроить)

---

## Лицензия

Proprietary - All rights reserved

Документы (государственные стандарты) принадлежат Республике Узбекистан.

---

**Последнее обновление**: 2026-05-02

**Версия**: 2.0.0
