# История изменений

Все важные изменения проекта будут документированы в этом файле.

## [0.4.0] - 2026-03-15

### Добавлено (AI-помощник и Windows setup)

#### AI-помощник на главной странице
- **Frontend компонент AIAssistant**:
  - Плавающая кнопка 🤖 в правом нижнем углу
  - Чат-окно с историей сообщений
  - Поддержка markdown, таблиц HTML, изображений
  - Отображение источников (sources) из RAG
  - Анимация загрузки (typing dots)
  - Адаптивный дизайн для мобильных устройств

- **Backend интеграция**:
  - Прокси-эндпоинт `/api/ai/chat` в Flask
  - Проксирование запросов к Django AI backend
  - Обработка ошибок и таймаутов (60 секунд)
  - Конфигурация через `AI_BACKEND_URL` в .env

- **Django AI Backend** (shnq_ai_backend):
  - RAG (Retrieval-Augmented Generation) для вопросов по стандартам
  - DeepSeek API для LLM и embeddings
  - Поддержка 4 языков (узбекский, русский, английский, корейский)
  - Векторный поиск через Qdrant или PostgreSQL
  - Извлечение таблиц, изображений из документов
  - Few-shot learning для улучшения ответов
  - SQLite база с моделями: Document, Chapter, Clause, NormTable, NormImage

#### Обновлённая документация
- **README.md**:
  - Полностью переписан для Windows (PowerShell)
  - Пошаговые инструкции для 2-3 терминалов
  - Секция быстрого старта с копипастой команд
  - Описание AI-помощника (опционально)
  - Таблица API с `/api/ai/chat`
  - Обновлён технологический стек

- **AI-ready-project/WINDOWS_SETUP.md**:
  - Инструкция по запуску Django AI backend
  - Настройка DeepSeek API ключа
  - Troubleshooting и FAQ
  - Загрузка документов через админку

#### Конфигурация
- Добавлен `AI_BACKEND_URL` в config.py и .env.example
- Значение по умолчанию: `http://localhost:8000`

#### Требования
- Python 3.12+ (рекомендуется 3.14)
- Django 6.0 + DRF для AI backend
- DeepSeek API ключ (для AI функционала)
- Опционально: Qdrant для векторного поиска

### Файловая структура
```
frontend/src/components/
├── AIAssistant.jsx          # React компонент AI-чата
└── AIAssistant.css          # Стили с градиентами и анимациями

backend/app/routes/
└── ai.py                    # Прокси для Django AI backend

AI-ready-project/
├── WINDOWS_SETUP.md         # Инструкция для Windows
└── shnq_ai_backend/         # Django проект с RAG
```

### Примечания
- AI-помощник работает только если запущен Django backend на :8000
- Без DeepSeek API можно использовать fallback на sentence-transformers
- Чат доступен на главной странице для всех пользователей
- Ответы кэшируются в QuestionAnswer модели

## [0.3.0] - 2026-02-19

### Добавлено (Интеграция платежных систем)

#### Платежные сервисы
- **Click**: Полная интеграция с Click.uz
  - Создание платежа через redirect метод
  - Обработка prepare (action=0) и complete (action=1) callbacks
  - Проверка подписи HMAC-SHA1
  - Конфигурация: CLICK_MERCHANT_ID, CLICK_SERVICE_ID, CLICK_SECRET_KEY

- **PayMe**: Полная интеграция с PayMe (Payme)
  - Создание платежа через checkout URL
  - JSON-RPC 2.0 протокол для callbacks
  - Поддержка всех RPC методов:
    - CheckPerformTransaction - проверка возможности оплаты
    - CreateTransaction - создание транзакции (резервирование)
    - PerformTransaction - выполнение транзакции (списание)
    - CancelTransaction - отмена транзакции
    - CheckTransaction - проверка статуса
  - Управление состояниями транзакций (created, completed, cancelled)
  - Конфигурация: PAYME_MERCHANT_ID, PAYME_SECRET_KEY

- **Банковские карты**: Интеграция через агрегатор (Uzcard/Humo)
  - Универсальная реализация для работы с различными агрегаторами
  - Поддержка: Apelsin, Payze, Octo и др.
  - Создание платежа через API агрегатора
  - Проверка подписи HMAC-SHA256
  - Обработка success/failed callbacks
  - Возврат средств (refund) - полный и частичный
  - Конфигурация: CARD_MERCHANT_ID, CARD_SECRET_KEY, CARD_API_URL

#### Backend обновления
- Обновлен `/api/payments/create`:
  - Автоматический выбор сервиса по payment_method (click/payme/card)
  - Создание платежа в платежной системе
  - Возврат payment_url для редиректа пользователя
  - Сохранение transaction_id и payment_url в БД

- Новые webhook эндпоинты:
  - `POST /api/payments/callback/click` - для Click (form data)
  - `POST /api/payments/callback/payme` - для PayMe (JSON-RPC)
  - `POST /api/payments/callback/card` - для карточного агрегатора (JSON)

- Обработка callbacks:
  - Валидация подписи от платежной системы
  - Обновление статуса Purchase и Payment
  - Сохранение callback_data для аудита
  - Предотвращение дублирования платежей

- Модель Payment:
  - `payment_url` - URL для оплаты
  - `transaction_id` - ID транзакции в платежной системе
  - `callback_data` - JSON данные от платежной системы
  - Поддержка статусов: pending, completed, failed, cancelled

#### Конфигурация
- Расширен `config.py` для платежных систем (9 новых параметров)
- Обновлен `.env.example` с подробными комментариями и ссылками
- Добавлена библиотека `requests==2.31.0` для HTTP запросов

#### Документация
- **PAYMENT_INTEGRATION.md** - полное руководство по интеграции (500+ строк):
  - Регистрация в платежных системах
  - Настройка webhook URL
  - Получение API ключей
  - Тестирование с тестовыми картами
  - Примеры использования сервисов
  - Описание протоколов (Click, PayMe JSON-RPC, Card API)
  - Troubleshooting и решение типовых проблем
  - Безопасность (проверка подписей, IP whitelist)
  - Полезные ссылки на документацию

- Обновлен README.md:
  - Секция "Платежные системы" с кратким обзором
  - Инструкции по настройке
  - Обновлены API endpoints для платежей

#### Файловая структура
```
backend/app/services/
├── click_service.py    # Click integration
├── payme_service.py    # PayMe JSON-RPC integration
└── card_service.py     # Card aggregator integration
```

### Примечания
- Сервисы готовы к использованию после получения API ключей
- PayMe использует JSON-RPC 2.0 - требует специальной обработки
- Card service - универсальный, требует адаптации под конкретного агрегатора
- Все платежи логируются в БД для аудита
- Поддержка тестовых и production режимов

## [0.2.0] - 2026-02-19

### Изменено (Backend: Node.js -> Flask)
- **Удален** Node.js + Express backend
- **Создан** новый легковесный backend на Python Flask
- Ценообразование: 1 страница = 1 000 сум (настраивается через `PRICE_PER_PAGE`)

### Архитектура Production
- **Backend**: DigitalOcean Droplet (Flask + PostgreSQL)
- **Файлы**: QNAP NAS в офисе (статический IP)
- **Подключение**: NFS mount от Droplet к QNAP для чтения PDF/Word
- **Создан подробный гайд**: [DROPLET_DEPLOYMENT.md](./DROPLET_DEPLOYMENT.md) - 10 частей, 600+ строк

#### Backend (Flask)
- REST API на Flask с Flask-SQLAlchemy ORM
- JWT аутентификация (flask-jwt-extended)
- Эндпоинты:
  - `POST /api/auth/register` и `/api/auth/login` - регистрация и вход
  - `GET /api/documents` - список документов с поиском и фильтрацией
  - `GET /api/documents/<id>` - детали документа + статус покупки
  - `GET /api/documents/<id>/preview` - PDF превью (первые 2 страницы, PyMuPDF)
  - `GET /api/documents/<id>/download` - скачивание полного документа (после оплаты)
  - `POST /api/payments/create` - создание платежа
  - `POST /api/payments/callback/<system>` - webhook для платежных систем
  - `GET /api/users/purchases` - купленные документы пользователя
- Модели: User, Document, Purchase, Payment
- Сервис для вырезки первых 2 страниц PDF (PyMuPDF)
- Seed-скрипт для начального наполнения БД (10 документов + админ)
- Gunicorn для production, Dockerfile

#### Frontend
- Подключен к реальному API (вместо mock-данных)
- AuthContext для управления состоянием аутентификации
- Навигация показывает имя пользователя / кнопку выхода
- Documents.jsx: загрузка документов и категорий с сервера
- DocumentPreview.jsx: загрузка с API, отображение PDF превью через iframe
- Login/Signup: реальная авторизация через API с обработкой ошибок
- Vite proxy для проксирования `/api` на Flask (dev-режим)

#### Инфраструктура
- Обновлен docker-compose.yml под Flask (порт 5000)
- Убран Redis (не нужен для легковесного бека)
- PostgreSQL 15 для хранения данных

### Технические детали
- **Frontend**: React 18 + Vite
- **Backend**: Python 3.12 + Flask + Gunicorn
- **Database**: PostgreSQL 15
- **ORM**: Flask-SQLAlchemy
- **Auth**: JWT (flask-jwt-extended)
- **PDF**: PyMuPDF (fitz)
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **Язык интерфейса**: Русский

### Структура проекта
```
building-standard-website/
├── frontend/              # React приложение
│   ├── src/
│   │   ├── components/   # Компоненты (Navigation)
│   │   ├── pages/        # Страницы
│   │   ├── utils/        # API helper, AuthContext
│   │   └── App.jsx
│   └── package.json
│
├── backend/              # Flask API
│   ├── app/
│   │   ├── models/      # SQLAlchemy модели
│   │   ├── routes/      # API эндпоинты
│   │   └── services/    # Сервис работы с PDF
│   ├── run.py           # Dev entry point
│   ├── wsgi.py          # Production entry point (gunicorn)
│   ├── seed.py          # Наполнение БД начальными данными
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml   # Оркестрация контейнеров
├── QNAP_SETUP_GUIDE.md
├── CHANGELOG.md
└── README.md
```

## [0.1.0] - 2026-01-09

### Первая версия
- Базовая структура фронтенд приложения
- Функциональность предпросмотра документов
- UI для регистрации и авторизации пользователей
