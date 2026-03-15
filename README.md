# Платформа Государственных Стандартов РУз

Веб-платформа для продажи государственных строительных стандартов Республики Узбекистан, переведённых на русский язык.

Клиенты могут бесплатно просмотреть первые 2 страницы любого документа, а после оплаты получают полный доступ. Цена рассчитывается автоматически: **1 страница = 1 000 сум**.

---

## Архитектура

```
  Пользователь (браузер)
        │
        ▼
┌─────────────────────────────────────────────────┐
│             DigitalOcean Droplet                │
│                                                 │
│   Nginx :80/:443                                │
│     ├── /           → React SPA (статика)       │
│     └── /api/*      → Flask :5000               │
│                                                 │
│   Flask API                                     │
│     ├── JWT аутентификация                      │
│     ├── Каталог документов                      │
│     ├── PDF-превью (PyMuPDF)                    │
│     └── Платежи (Click, PayMe, Uzcard/Humo)     │
│                                                 │
│   PostgreSQL :5432                              │
│     └── users, documents, purchases, payments   │
│                                                 │
│   /mnt/qnap-documents ◄── NFS mount            │
└────────────────────────────┬────────────────────┘
                             │
                         NFS (TCP)
                             │
                    ┌────────┴────────┐
                    │  Офис (QNAP NAS)│
                    │  TS-433          │
                    │  PDF/Word файлы  │
                    │  Статический IP  │
                    └─────────────────┘
```

---

## Технологический стек

| Компонент   | Технология                                 |
|-------------|--------------------------------------------|
| Frontend    | React 19 + Vite 7 + React Router 7         |
| Backend     | Python 3.12+ + Flask 3.1 + Gunicorn        |
| AI Backend  | Django 6.0 + DeepSeek AI + RAG             |
| Database    | PostgreSQL 15                               |
| ORM         | Flask-SQLAlchemy 3.1                        |
| Auth        | JWT (flask-jwt-extended)                    |
| PDF-превью  | PyMuPDF (извлечение первых 2 страниц)      |
| Оплата      | Click, PayMe, банковские карты (Uzcard/Humo)|
| AI-помощник | DeepSeek, Sentence-Transformers, Qdrant    |
| Deploy      | Docker Compose + Nginx                      |
| Файлы       | QNAP NAS TS-433 через NFS                  |

---

## Быстрый старт (Windows)

### Требования

- **Node.js 18+** — https://nodejs.org/
- **Python 3.12+** (рекомендуется 3.14) — https://www.python.org/downloads/
- **PostgreSQL 15+** — https://www.postgresql.org/download/windows/

---

### Запуск проекта (2 терминала)

#### Терминал 1: Flask Backend (порт 5000)

```powershell
# 1. Откройте PowerShell в папке проекта
cd backend

# 2. Создайте виртуальное окружение
python -m venv venv

# 3. Активируйте виртуальное окружение
.\venv\Scripts\Activate.ps1

# 4. Обновите pip (важно!)
python -m pip install --upgrade pip

# 5. Установите зависимости (совместимы с Python 3.14)
pip install -r requirements-windows.txt

# 6. Создайте файл .env (скопируйте из примера)
copy .env.example .env

# 7. Отредактируйте .env в блокноте
notepad .env
# Укажите данные PostgreSQL:
#   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/standards_db
# (Замените второй 'postgres' на ваш пароль PostgreSQL)

# 8. Создайте базу данных через psql

# Найдите psql.exe (обычно в C:\Program Files\PostgreSQL\XX\bin или D:\PostgreSQL\bin)
# Быстрый способ найти:
# Get-ChildItem "C:\" -Recurse -Filter psql.exe -ErrorAction SilentlyContinue
# ИЛИ
# Get-ChildItem "D:\" -Recurse -Filter psql.exe -ErrorAction SilentlyContinue

# Перейдите в папку с psql и создайте БД:
cd "D:\PostgreSQL\bin"  # Замените на ваш путь к PostgreSQL
.\psql -U postgres
# Введите пароль PostgreSQL
# В консоли psql выполните:
#   CREATE DATABASE standards_db;
#   \q  (для выхода)

# 9. Инициализируйте таблицы и тестовые данные
python seed.py

# 10. Запустите Flask backend
python run.py
```

**Flask запустится на http://localhost:5000**

Тестовый админ:
- **Email**: `admin@standards.uz`
- **Пароль**: `admin123`

---

#### Терминал 2: React Frontend (порт 5173)

```powershell
# 1. Откройте ВТОРОЙ PowerShell в папке проекта
cd frontend

# 2. Установите зависимости (только первый раз)
npm install

# 3. Запустите dev-сервер
npm run dev
```

**Frontend откроется на http://localhost:5173**

Запросы `/api/*` автоматически проксируются на Flask backend.

---

#### (Опционально) Терминал 3: AI-помощник (порт 8000)

Для работы AI-помощника на главной странице:

```powershell
# 1. Откройте ТРЕТИЙ PowerShell
cd AI-ready-project\shnq_ai_backend

# 2. Создайте виртуальное окружение
python -m venv venv

# 3. Активируйте
.\venv\Scripts\Activate.ps1

# 4. Установите зависимости Django
pip install django djangorestframework django-cors-headers openai python-dotenv

# 5. Настройте DeepSeek API (нужен ключ)
$env:DEEPSEEK_API_KEY="ваш_api_ключ"
$env:DEEPSEEK_BASE_URL="https://api.deepseek.com"

# 6. Примените миграции
python manage.py migrate

# 7. Запустите Django backend
python manage.py runserver
```

**Django AI backend запустится на http://localhost:8000**

> **Примечание**: AI-помощник работает только при запущенном Django backend. Если он не нужен, можно не запускать.

---

### Готово!

Откройте http://localhost:5173 в браузере. На главной странице появится кнопка 🤖 AI-помощника (если Django запущен).

---

### Остановка серверов

Нажмите `Ctrl+C` в каждом терминале, чтобы остановить серверы.

---

## Troubleshooting (Windows)

### Ошибка: "execution policy" при активации venv

**Решение**: Разрешите выполнение скриптов
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Ошибка: "Could not connect to PostgreSQL"

**Проверьте**:
1. PostgreSQL запущен (проверьте Services)
2. Пароль в `.env` правильный
3. База данных `standards_db` создана:
```powershell
psql -U postgres
CREATE DATABASE standards_db;
\q
```

### Frontend не запускается

**Решение**:
```powershell
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## API

### Аутентификация

| Метод | URL                  | Описание              |
|-------|----------------------|-----------------------|
| POST  | `/api/auth/register` | Регистрация           |
| POST  | `/api/auth/login`    | Вход                  |
| GET   | `/api/auth/me`       | Текущий пользователь  |

### Документы

| Метод | URL                             | Описание                              |
|-------|---------------------------------|---------------------------------------|
| GET   | `/api/documents`                | Список (?search=, ?category=, ?page=) |
| GET   | `/api/documents/categories`     | Список категорий                      |
| GET   | `/api/documents/<id>`           | Детали документа                      |
| GET   | `/api/documents/<id>/preview`   | PDF первых 2 страниц                  |
| GET   | `/api/documents/<id>/download`  | Полный документ (после оплаты)        |

### Платежи

| Метод | URL                                | Описание                     |
|-------|------------------------------------|------------------------------|
| POST  | `/api/payments/create`             | Создать платёж → payment_url |
| POST  | `/api/payments/callback/click`     | Webhook Click                |
| POST  | `/api/payments/callback/payme`     | Webhook PayMe (JSON-RPC)     |
| POST  | `/api/payments/callback/card`      | Webhook карточный агрегатор  |
| GET   | `/api/payments/status/<id>`        | Статус платежа               |
| GET   | `/api/payments/history`            | История платежей             |

### Пользователь

| Метод | URL                    | Описание             |
|-------|------------------------|----------------------|
| GET   | `/api/users/profile`   | Профиль              |
| PUT   | `/api/users/profile`   | Обновить профиль     |
| PUT   | `/api/users/password`  | Сменить пароль       |
| GET   | `/api/users/purchases` | Купленные документы  |

### AI-помощник

| Метод | URL             | Описание                                |
|-------|-----------------|-----------------------------------------|
| POST  | `/api/ai/chat`  | Задать вопрос AI по стандартам (RAG)    |

**Пример запроса:**
```json
POST /api/ai/chat
{
  "message": "Что говорится в пункте 38 SHNQ 3.01.02-23?"
}
```

**Пример ответа:**
```json
{
  "answer": "38. Qurilish obyektlarida...",
  "sources": [{...}],
  "table_html": "...",
  "image_urls": [...],
  "meta": {...}
}
```

> **Требуется**: Запущенный Django AI backend на порту 8000

---

## Платёжные системы

| Метод            | Протокол      | Webhook URL                          |
|------------------|---------------|--------------------------------------|
| **Click**        | HMAC-SHA1     | `/api/payments/callback/click`       |
| **PayMe**        | JSON-RPC 2.0  | `/api/payments/callback/payme`       |
| **Uzcard/Humo**  | HMAC-SHA256   | `/api/payments/callback/card`        |

### Настройка

1. Зарегистрируйтесь в платёжных системах:
   - Click — https://my.click.uz/
   - PayMe — https://checkout.paycom.uz/
   - Агрегатор для карт (Apelsin, Payze, Octo и др.)

2. Добавьте ключи в `backend/.env`:

```env
CLICK_MERCHANT_ID=...
CLICK_SERVICE_ID=...
CLICK_SECRET_KEY=...

PAYME_MERCHANT_ID=...
PAYME_SECRET_KEY=...

CARD_MERCHANT_ID=...
CARD_SECRET_KEY=...
CARD_API_URL=https://api.your-aggregator.uz
```

3. Укажите webhook URL в личных кабинетах платёжных систем

Подробнее: **[PAYMENT_INTEGRATION.md](./PAYMENT_INTEGRATION.md)**

---

## Структура проекта

```
building-standard-website/
│
├── frontend/                          # React SPA
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navigation.jsx         # Навигация
│   │   │   └── Navigation.css
│   │   ├── pages/
│   │   │   ├── Home.jsx               # Главная страница
│   │   │   ├── Documents.jsx          # Каталог документов
│   │   │   ├── DocumentPreview.jsx    # Превью + покупка
│   │   │   ├── Login.jsx              # Вход
│   │   │   └── Signup.jsx             # Регистрация
│   │   ├── utils/
│   │   │   ├── api.js                 # HTTP-клиент с JWT
│   │   │   └── AuthContext.jsx        # React Context авторизации
│   │   ├── App.jsx                    # Роутинг
│   │   └── main.jsx                   # Точка входа
│   ├── vite.config.js                 # Dev proxy /api → :5000
│   └── package.json
│
├── backend/                           # Flask API
│   ├── app/
│   │   ├── __init__.py                # App factory
│   │   ├── config.py                  # Конфигурация (env vars)
│   │   ├── models/
│   │   │   ├── user.py                # Пользователь
│   │   │   ├── document.py            # Документ + динамическая цена
│   │   │   ├── purchase.py            # Покупка
│   │   │   └── payment.py             # Платёж
│   │   ├── routes/
│   │   │   ├── auth.py                # Регистрация, вход
│   │   │   ├── documents.py           # Каталог, превью, скачивание
│   │   │   ├── payments.py            # Платежи, webhooks
│   │   │   └── users.py               # Профиль, покупки
│   │   └── services/
│   │       ├── file_service.py        # PDF-превью (PyMuPDF)
│   │       ├── click_service.py       # Click
│   │       ├── payme_service.py       # PayMe (JSON-RPC)
│   │       └── card_service.py        # Uzcard/Humo
│   ├── run.py                         # Dev-сервер
│   ├── wsgi.py                        # Gunicorn entry point
│   ├── seed.py                        # Тестовые данные
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── docker-compose.yml                 # PostgreSQL + Flask + Nginx
├── DROPLET_DEPLOYMENT.md              # Деплой на DigitalOcean + QNAP NFS
├── PAYMENT_INTEGRATION.md             # Интеграция платёжных систем
├── QNAP_SETUP_GUIDE.md               # Настройка QNAP NAS
├── CHANGELOG.md                       # История изменений
└── README.md
```

---

## Добавление документов

1. Загрузите PDF/Word файл на QNAP в папку `standards-documents`
2. Добавьте запись в БД с указанием `file_path` (имя файла)
3. Превью первых 2 страниц генерируется автоматически при запросе

---

## Развёртывание на Production

**Сервер**: DigitalOcean Droplet + NFS-подключение к QNAP NAS в офисе.

Подробное руководство: **[DROPLET_DEPLOYMENT.md](./DROPLET_DEPLOYMENT.md)**

Краткий план:

1. Настроить NFS-экспорт на QNAP
2. Создать Droplet на DigitalOcean
3. Смонтировать QNAP через NFS (`/mnt/qnap-documents`)
4. Развернуть приложение через Docker Compose
5. Настроить SSL (Let's Encrypt) и домен

---

## Переменные окружения

| Переменная           | Описание                         | По умолчанию                |
|----------------------|----------------------------------|-----------------------------|
| `SECRET_KEY`         | Секрет Flask                     | `dev-secret-key`            |
| `JWT_SECRET_KEY`     | Секрет JWT                       | `dev-jwt-secret`            |
| `DATABASE_URL`       | PostgreSQL connection string     | `postgresql://...localhost` |
| `UPLOAD_FOLDER`      | Путь к файлам документов         | `uploads/documents`         |
| `PRICE_PER_PAGE`     | Цена за страницу (сум)           | `1000`                      |
| `FRONTEND_URL`       | URL фронтенда (CORS)            | `http://localhost:5173`     |
| `CLICK_MERCHANT_ID`  | Click Merchant ID                | —                           |
| `CLICK_SERVICE_ID`   | Click Service ID                 | —                           |
| `CLICK_SECRET_KEY`   | Click Secret Key                 | —                           |
| `PAYME_MERCHANT_ID`  | PayMe Merchant ID                | —                           |
| `PAYME_SECRET_KEY`   | PayMe Secret Key                 | —                           |
| `CARD_MERCHANT_ID`   | Card Merchant ID                 | —                           |
| `CARD_SECRET_KEY`    | Card Secret Key                  | —                           |
| `CARD_API_URL`       | Card aggregator API URL          | —                           |

Все переменные задаются в `backend/.env` (пример: `backend/.env.example`).

---

## Документация

| Файл                                                    | Описание                                |
|---------------------------------------------------------|-----------------------------------------|
| [README.md](./README.md)                               | Общее описание проекта                  |
| [DROPLET_DEPLOYMENT.md](./DROPLET_DEPLOYMENT.md)       | Деплой на DigitalOcean + QNAP (10 частей)|
| [PAYMENT_INTEGRATION.md](./PAYMENT_INTEGRATION.md)     | Интеграция Click, PayMe, карт           |
| [QNAP_SETUP_GUIDE.md](./QNAP_SETUP_GUIDE.md)         | Настройка QNAP NAS                     |
| [CHANGELOG.md](./CHANGELOG.md)                         | История изменений                       |
