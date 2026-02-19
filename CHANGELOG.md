# История изменений

Все важные изменения проекта будут документированы в этом файле.

## [0.2.0] - 2026-02-19

### Изменено (Backend: Node.js -> Flask)
- **Удален** Node.js + Express backend
- **Создан** новый легковесный backend на Python Flask
- Ценообразование: 1 страница = 1 000 сум (настраивается через `PRICE_PER_PAGE`)

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
