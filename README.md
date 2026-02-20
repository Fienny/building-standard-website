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
| Backend     | Python 3.12 + Flask 3.1 + Gunicorn         |
| Database    | PostgreSQL 15                               |
| ORM         | Flask-SQLAlchemy 3.1                        |
| Auth        | JWT (flask-jwt-extended)                    |
| PDF-превью  | PyMuPDF (извлечение первых 2 страниц)      |
| Оплата      | Click, PayMe, банковские карты (Uzcard/Humo)|
| Deploy      | Docker Compose + Nginx                      |
| Файлы       | QNAP NAS TS-433 через NFS                  |

---

## Быстрый старт (development)

### Требования

- Node.js 18+
- Python 3.10+
- PostgreSQL 15+

### 1. Frontend

```bash
cd frontend
npm install
npm run dev
```

Откроется на `http://localhost:5173`. Запросы `/api/*` проксируются на Flask через Vite.

### 2. Backend

```bash
cd backend

# Виртуальное окружение
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Зависимости
pip install -r requirements.txt

# Конфигурация
cp .env.example .env
# Отредактируйте .env — укажите данные БД и ключи платёжных систем

# Запуск
python run.py
```

Backend запустится на `http://localhost:5000`.

### 3. Инициализация БД

```bash
cd backend
python seed.py
```

Создаст таблицы и добавит 10 тестовых документов + администратора:

- **Логин**: `admin@standards.uz`
- **Пароль**: `admin123`

### 4. Docker Compose

```bash
docker-compose up -d --build
```

Поднимет PostgreSQL, Flask backend и Nginx. Сайт доступен на порту 80.

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
