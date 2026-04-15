# Локальный запуск и тестирование проекта

> Дата: 2026-04-15  
> Этот документ описывает практический сценарий запуска и проверки проекта на локальной машине.

## 1) Что поднимаем

Проект состоит из 4 сервисов:

1. `frontend` — React + Nginx (UI)
2. `backend` — Flask API (документы, auth, платежи, прокси к AI)
3. `ai-backend` — Django AI сервис (RAG/чат)
4. `postgres` — основная БД

## 2) Быстрый старт через Docker (рекомендуется)

### 2.1. Требования
- Docker Desktop 4+
- Docker Compose

### 2.2. Подготовка `.env`
Из корня репозитория:

```bash
cp .env.docker .env
```

Проверьте минимум:

- `DB_PASSWORD`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DEEPSEEK_API_KEY` (или OpenAI-совместимый ключ)

### 2.3. Запуск

```bash
docker-compose up -d --build
```

### 2.4. Проверка здоровья

```bash
docker-compose ps
docker-compose logs -f backend
docker-compose logs -f ai-backend
docker-compose logs -f frontend
```

Ожидаемые адреса:

- Frontend: `http://localhost`
- Backend API: `http://localhost:5000`
- AI backend: `http://localhost:8000`

## 3) Локальный запуск без Docker (для разработки)

## 3.1 Backend (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
python run.py
```

## 3.2 AI backend (Django)

```bash
cd AI-ready-project/shnq_ai_backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## 3.3 Frontend

```bash
cd frontend
npm ci
npm run dev
```

## 4) Минимальный smoke-check перед демонстрацией

### 4.1 UI / Документы

1. Открыть `/documents`
2. Проверить поиск и фильтры категорий
3. Открыть карточку документа `/documents/:id`
4. Проверить превью первых 2 страниц

### 4.2 Покупка (без боевого провайдера)

1. На странице документа выбрать метод оплаты
2. Нажать «Создать платеж»
3. Убедиться, что появляется ссылка `payment_url`
4. Проверить страницы:
   - `/payment/success`
   - `/payment/failed`
   - `/payment/pending`

### 4.3 AI ассистент

1. Открыть виджет AI
2. Отправить 3 разных вопроса (общий, по конкретному SHNQ, по таблице)
3. Проверить:
   - ответ приходит,
   - отображаются источники,
   - при задержке ответа показывается hint,
   - после перезагрузки история чата сохраняется.

## 5) Команды тестирования

### Frontend

```bash
cd frontend
npm run lint
npm run build
```

> В текущем состоянии `npm run lint` может падать на существующих правилах в `src/utils/AuthContext.jsx` (не связано с запуском приложения).

### Backend базовый health

```bash
curl -s http://localhost:5000/api/health
```

Ожидаемый ответ:

```json
{"status":"OK"}
```

## 6) Проверка загрузки архива документов (~140 файлов)

Используйте ранее добавленную инструкцию:
- `AI_TRAINING_DATA_PREPARATION.md`

Краткий pipeline:

```bash
python scripts/normalize_documents.py ./documents-archive/source ./documents-normalized
python scripts/bulk_upload.py ./documents-normalized/normalized
# либо без AI:
python scripts/bulk_upload.py ./documents-normalized/normalized --no-ai
```

## 7) Частые проблемы

1. `AI backend недоступен`
   - проверьте, что Django сервис поднят на `:8000`
   - проверьте `AI_BACKEND_URL` в backend

2. `Пустое превью PDF`
   - убедитесь, что файл существует в `UPLOAD_FOLDER`
   - проверьте, что PDF не поврежден

3. `Ошибка конвертации DOC/DOCX`
   - установите LibreOffice
   - проверьте доступность команды `libreoffice --version`

## 8) Рекомендация по процессу для команды

Перед каждым merge в рабочую ветку:

1. `npm run build` (frontend)
2. Проверка `/api/health` (backend)
3. Smoke-check из раздела 4
4. Обновление `codex.md` (что сделали/риски/next steps)
