# Платформа Государственных Стандартов РУз

Веб-платформа для продажи государственных стандартов Республики Узбекистан, переведенных на русский язык.

## Описание проекта

Клиенты могут бесплатно просмотреть первые 2 страницы любого документа, а после оплаты получают полный доступ. Цена рассчитывается автоматически: **1 страница = 1 000 сум**.

### Архитектура

- **Backend**: развернут на DigitalOcean Droplet
- **Database**: PostgreSQL на том же Droplet
- **Файлы**: хранятся на QNAP NAS в офисе (статический IP)
- **Подключение**: Droplet монтирует QNAP через NFS для чтения PDF/Word

```
DigitalOcean Droplet          Офис (QNAP NAS)
┌─────────────────┐           ┌──────────────┐
│ Nginx + Flask   │           │   PDF/Word   │
│ + PostgreSQL    │◄─── NFS ──┤   документы  │
└─────────────────┘           └──────────────┘
```

## Технологический стек

| Компонент | Технология |
|-----------|-----------|
| Frontend | React 18 + Vite |
| Backend | Python 3.12 + Flask |
| Database | PostgreSQL 15 |
| ORM | Flask-SQLAlchemy |
| Auth | JWT (flask-jwt-extended) |
| PDF | PyMuPDF (превью первых 2 страниц) |
| Deploy | Docker Compose + Nginx |
| Server | QNAP NAS TS-433 |
| Оплата | Click, PayMe, банковские карты |

## Быстрый старт

### Требования
- Node.js 18+
- Python 3.10+
- PostgreSQL 15+

### 1. Frontend (dev-режим)

```bash
cd frontend
npm install
npm run dev
```

Откроется на `http://localhost:5173`. Запросы к `/api` проксируются на Flask.

### 2. Backend (dev-режим)

```bash
cd backend

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Установите зависимости
pip install -r requirements.txt

# Создайте файл .env (скопируйте из примера и отредактируйте)
cp .env.example .env

# Запустите сервер
python run.py
```

Backend запустится на `http://localhost:5000`.

### 3. Инициализация базы данных

```bash
cd backend
python seed.py
```

Создаст таблицы, добавит 10 тестовых документов и администратора:
- **Админ**: `admin@standards.uz` / `admin123`

### 4. Docker Compose (production)

```bash
docker-compose up -d --build
```

Запустит PostgreSQL, Flask backend и Nginx. Сайт будет доступен на порту 80.

## API эндпоинты

### Аутентификация
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | Вход |
| GET | `/api/auth/me` | Текущий пользователь |

### Документы
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/documents` | Список документов (?search=, ?category=) |
| GET | `/api/documents/categories` | Список категорий |
| GET | `/api/documents/<id>` | Детали документа |
| GET | `/api/documents/<id>/preview` | PDF первых 2 страниц |
| GET | `/api/documents/<id>/download` | Скачать полный документ (после оплаты) |

### Платежи
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/payments/create` | Создать платеж (вернет payment_url) |
| POST | `/api/payments/callback/click` | Webhook от Click |
| POST | `/api/payments/callback/payme` | Webhook от PayMe (JSON-RPC) |
| POST | `/api/payments/callback/card` | Webhook от карточного агрегатора |
| GET | `/api/payments/status/<id>` | Статус платежа |
| GET | `/api/payments/history` | История платежей пользователя |

### Пользователь
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/users/profile` | Профиль |
| PUT | `/api/users/profile` | Обновить профиль |
| PUT | `/api/users/password` | Сменить пароль |
| GET | `/api/users/purchases` | Купленные документы |

## Структура проекта

```
building-standard-website/
├── frontend/                  # React приложение
│   ├── src/
│   │   ├── components/       # Navigation
│   │   ├── pages/            # Home, Documents, DocumentPreview, Login, Signup
│   │   └── utils/            # api.js, AuthContext.jsx
│   ├── vite.config.js        # Proxy /api -> localhost:5000
│   └── package.json
│
├── backend/                   # Flask API
│   ├── app/
│   │   ├── models/           # User, Document, Purchase, Payment
│   │   ├── routes/           # auth, documents, payments, users
│   │   └── services/         # file_service, click_service, payme_service, card_service
│   ├── run.py                # Dev entry point
│   ├── wsgi.py               # Gunicorn entry point
│   ├── seed.py               # Seed data
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
├── DROPLET_DEPLOYMENT.md     # Руководство по развертыванию на DigitalOcean
├── PAYMENT_INTEGRATION.md    # Руководство по интеграции платежных систем
├── CHANGELOG.md
└── README.md
```

## Платежные системы

Платформа поддерживает три метода оплаты:

- **Click** - популярная платежная система в Узбекистане
- **PayMe** - платежная система от Payme
- **Банковские карты** - Uzcard/Humo через агрегатор (Apelsin, Payze, Octo и т.д.)

### Настройка платежных систем

1. Зарегистрируйтесь в выбранных платежных системах:
   - Click: https://my.click.uz/
   - PayMe: https://checkout.paycom.uz/
   - Агрегатор для карт (например, Apelsin: https://apelsin.uz/)

2. Получите API ключи и добавьте их в `.env`:

```bash
# Click
CLICK_MERCHANT_ID=your_merchant_id
CLICK_SERVICE_ID=your_service_id
CLICK_SECRET_KEY=your_secret_key

# PayMe
PAYME_MERCHANT_ID=your_merchant_id
PAYME_SECRET_KEY=your_secret_key

# Card
CARD_MERCHANT_ID=your_merchant_id
CARD_SECRET_KEY=your_secret_key
CARD_API_URL=https://api.your-aggregator.uz
```

3. Настройте webhook URL в личных кабинетах:
   - Click: `https://yourdomain.uz/api/payments/callback/click`
   - PayMe: `https://yourdomain.uz/api/payments/callback/payme`
   - Card: `https://yourdomain.uz/api/payments/callback/card`

**Подробное руководство**: [PAYMENT_INTEGRATION.md](./PAYMENT_INTEGRATION.md)

## Добавление документов

1. Положите PDF файл на QNAP в папку `standards-documents`
2. Обновите запись в БД, указав `file_path` (имя файла)
3. Превью (первые 2 страницы) генерируется автоматически при запросе

## Развертывание на Production

**Backend**: DigitalOcean Droplet + NFS подключение к QNAP

Подробное руководство: [DROPLET_DEPLOYMENT.md](./DROPLET_DEPLOYMENT.md)

Краткая последовательность:
1. Настроить QNAP NFS экспорт
2. Создать Droplet на DigitalOcean
3. Смонтировать QNAP через NFS
4. Развернуть приложение через Docker Compose
5. Настроить SSL и домен
