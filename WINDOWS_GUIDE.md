# 🪟 Полный гайд по запуску на Windows

Подробное руководство по запуску Standards Platform на Windows 10/11.

---

## 📋 Содержание

1. [Вариант 1: Docker (Рекомендуется)](#вариант-1-docker-рекомендуется)
2. [Вариант 2: Запуск без Docker](#вариант-2-запуск-без-docker)
3. [Troubleshooting](#troubleshooting)

---

## Вариант 1: Docker (Рекомендуется)

**Преимущества**:
- ✅ Запуск всего стека одной командой
- ✅ Не нужно устанавливать Python, PostgreSQL, Node.js вручную
- ✅ Полная изоляция от системы
- ✅ Одинаково работает на Windows/Mac/Linux

### Шаг 1: Установка Docker Desktop

1. **Скачайте Docker Desktop** для Windows:
   - https://www.docker.com/products/docker-desktop/

2. **Запустите установщик** и следуйте инструкциям

3. **После установки**:
   - Перезагрузите компьютер
   - Запустите Docker Desktop
   - Дождитесь запуска (иконка Docker в трее должна стать зеленой)

4. **Проверьте установку**:
   ```powershell
   docker --version
   docker-compose --version
   ```
   
   Должно вывести версии (например, `Docker version 24.0.7`).

### Шаг 2: Клонирование репозитория

```powershell
# Откройте PowerShell или Windows Terminal
# Перейдите в папку где хотите разместить проект (например, Documents)
cd ~\Documents

# Клонируйте репозиторий
git clone https://github.com/your-repo/building-standard-website.git
cd building-standard-website
```

### Шаг 3: Настройка переменных окружения

Файл `.env` уже создан в корне проекта, нужно только **добавить DeepSeek API ключ**.

#### 3.1 Получение DeepSeek API ключа (БЕСПЛАТНО)

1. Откройте https://platform.deepseek.com/
2. Зарегистрируйтесь (можно через Google/GitHub)
3. Перейдите в **API Keys**
4. Нажмите **Create new key**
5. Скопируйте ключ (начинается с `sk-`)

#### 3.2 Редактирование .env

```powershell
# Откройте .env в Блокноте
notepad .env
```

**Найдите строку**:
```env
DEEPSEEK_API_KEY=sk-YOUR-DEEPSEEK-API-KEY-HERE
```

**Замените на ваш ключ**:
```env
DEEPSEEK_API_KEY=sk-ваш-настоящий-ключ-здесь
```

**Сохраните** (Ctrl+S) и **закройте** Блокнот.

### Шаг 4: Запуск всего стека

```powershell
# Убедитесь что Docker Desktop запущен!
# Затем выполните:
docker-compose up -d --build
```

**Что происходит**:
- Скачиваются Docker образы (PostgreSQL, Qdrant, Alpine Linux)
- Собираются образы для Backend, AI Backend, Frontend
- Создаются контейнеры и networks
- Запускаются все 5 сервисов

**Первый запуск займет 5-10 минут** (зависит от скорости интернета).

### Шаг 5: Проверка работы

#### 5.1 Проверить что все контейнеры запущены

```powershell
docker-compose ps
```

**Должно показать**:
```
NAME                     STATUS
standards-db             Up (healthy)
standards-backend        Up
standards-ai-backend     Up
standards-qdrant         Up (healthy)
standards-frontend       Up
```

Если какой-то сервис показывает `Exit` или `Restarting`, смотрите логи:

```powershell
docker-compose logs -f backend
# Или
docker-compose logs -f ai-backend
```

#### 5.2 Открыть приложение в браузере

Откройте в браузере:

- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **AI Backend**: http://localhost:8000
- **Qdrant Dashboard**: http://localhost:6333/dashboard

### Шаг 6: Инициализация данных (опционально)

Backend автоматически создает таблицы при старте. Чтобы добавить **тестовые данные** (администратор + 10 документов):

```powershell
# Войдите в контейнер backend
docker exec -it standards-backend bash

# Запустите seed.py
python seed.py

# Выйдите из контейнера
exit
```

**Тестовый администратор**:
- Email: `admin@standards.uz`
- Пароль: `admin123`

### Шаг 7: Готово!

Теперь можно:
- Зарегистрироваться на сайте
- Войти как администратор
- Просматривать документы
- Покупать документы (тестовый режим)
- Задавать вопросы AI-помощнику

---

## 🛠️ Полезные Docker команды

### Просмотр логов

```powershell
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ai-backend
docker-compose logs -f postgres
docker-compose logs -f qdrant
```

### Остановка/запуск

```powershell
# Остановить все сервисы
docker-compose down

# Запустить снова
docker-compose up -d

# Перезапустить конкретный сервис
docker-compose restart backend
```

### Пересборка после изменений в коде

```powershell
# Пересобрать все сервисы
docker-compose up -d --build

# Пересобрать только backend
docker-compose up -d --build backend

# Пересобрать только frontend
docker-compose up -d --build frontend
```

### Удаление всех данных (ОСТОРОЖНО!)

```powershell
# Остановить и удалить контейнеры + volumes
docker-compose down -v

# Удалить все неиспользуемые образы, контейнеры, volumes
docker system prune -a --volumes
```

### Работа с базой данных

```powershell
# Подключиться к PostgreSQL
docker exec -it standards-db psql -U standards_user -d standards_db

# В psql консоли:
# \dt           - список таблиц
# \d users      - структура таблицы users
# SELECT COUNT(*) FROM documents;  - количество документов
# \q            - выход
```

### Войти в контейнер

```powershell
# Backend
docker exec -it standards-backend bash

# AI Backend
docker exec -it standards-ai-backend bash

# Frontend
docker exec -it standards-frontend sh
```

---

## Вариант 2: Запуск без Docker

Если Docker не подходит (старый компьютер, корпоративные ограничения и т.д.), можно запустить вручную.

### Требования

1. **Python 3.12 или выше** (рекомендуется 3.14)
   - Скачать: https://www.python.org/downloads/
   - ⚠️ При установке отметьте "Add Python to PATH"!

2. **Node.js 18 или выше** (рекомендуется 20 LTS)
   - Скачать: https://nodejs.org/

3. **PostgreSQL 15 или выше**
   - Скачать: https://www.postgresql.org/download/windows/
   - Запомните пароль для пользователя `postgres`!

4. **Git** (если еще не установлен)
   - Скачать: https://git-scm.com/download/win

### Проверка установки

```powershell
python --version    # Должно показать Python 3.12.x или выше
node --version      # Должно показать v18.x.x или выше
npm --version       # Должно показать 9.x.x или выше
psql --version      # Должно показать psql 15.x или выше
```

---

## Шаг 1: Клонирование проекта

```powershell
cd ~\Documents
git clone https://github.com/your-repo/building-standard-website.git
cd building-standard-website
```

---

## Шаг 2: Настройка PostgreSQL

### 2.1 Запустить PostgreSQL

1. Откройте **Services** (Win+R → `services.msc`)
2. Найдите **postgresql-x64-15** (или похожее)
3. Убедитесь что статус **Running**
4. Если не запущен: Right-click → **Start**

### 2.2 Создать базу данных

```powershell
# Найдите путь к psql.exe
# Обычно это C:\Program Files\PostgreSQL\15\bin или D:\PostgreSQL\bin

# Вариант 1: Если PostgreSQL в PATH
psql -U postgres

# Вариант 2: Если не в PATH, укажите полный путь
cd "C:\Program Files\PostgreSQL\15\bin"
.\psql -U postgres

# Введите пароль PostgreSQL
```

**В консоли psql** выполните:

```sql
-- Создать основную БД
CREATE DATABASE standards_db;

-- Создать БД для AI backend
CREATE DATABASE standards_ai_db;

-- Создать расширения
\c standards_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c standards_ai_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Выйти
\q
```

---

## Шаг 3: Backend (Flask API)

### 3.1 Открыть PowerShell в папке backend

```powershell
cd backend
```

### 3.2 Создать виртуальное окружение

```powershell
python -m venv venv
```

### 3.3 Активировать виртуальное окружение

```powershell
.\venv\Scripts\Activate.ps1
```

**Если ошибка "execution policy"**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Затем снова:
.\venv\Scripts\Activate.ps1
```

После активации должно появиться `(venv)` в начале строки:
```
(venv) PS C:\Users\...\backend>
```

### 3.4 Обновить pip

```powershell
python -m pip install --upgrade pip
```

### 3.5 Установить зависимости

```powershell
pip install -r requirements-windows.txt
```

**Примечание**: Используем `requirements-windows.txt` т.к. он содержит совместимые версии для Windows и Python 3.14.

### 3.6 Настроить .env

```powershell
# Скопировать пример
copy .env.example .env

# Открыть в Блокноте
notepad .env
```

**Минимальная конфигурация**:

```env
# Flask
FLASK_ENV=production
SECRET_KEY=ваш-случайный-секретный-ключ-здесь
JWT_SECRET_KEY=другой-случайный-секретный-ключ

# Database
DATABASE_URL=postgresql://postgres:ВАШ_ПАРОЛЬ@localhost:5432/standards_db

# Wasabi S3 (уже заполнено в примере, оставьте как есть)
WASABI_ACCESS_KEY_ID=4E3G3COQYUP8GFKQHSNA
WASABI_SECRET_ACCESS_KEY=lPGcfRHzsDeDzvZu80EtfeqC5XMLn8eqlMVNySLm
WASABI_BUCKET_NAME=standards
WASABI_REGION=eu-central-1

# Pricing
PRICE_PER_PAGE=1000

# Frontend URL (для CORS)
FRONTEND_URL=http://localhost:5173

# AI Backend (если запущен)
AI_BACKEND_URL=http://localhost:8000
```

**⚠️ ВАЖНО**:
- Замените `ВАШ_ПАРОЛЬ` на пароль PostgreSQL
- Замените `SECRET_KEY` и `JWT_SECRET_KEY` на случайные строки (минимум 32 символа)

**Сгенерировать случайный ключ**:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

**Сохраните** (Ctrl+S) и закройте.

### 3.7 Инициализировать БД и создать тестовые данные

```powershell
python seed.py
```

**Должно вывести**:
```
База данных инициализирована!
Создан администратор: admin@standards.uz
+ Документ: ОзДСт 2710:2019 ...
...
Готово! Seed завершен.
```

### 3.8 Запустить Flask backend

```powershell
python run.py
```

**Должно показать**:
```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

✅ **Backend запущен на http://localhost:5000**

**Не закрывайте этот терминал!** Flask должен продолжать работать.

---

## Шаг 4: Frontend (React + Vite)

### 4.1 Открыть ВТОРОЙ PowerShell

Не закрывая первый терминал с Flask, откройте **новый** PowerShell.

```powershell
cd ~\Documents\building-standard-website\frontend
```

### 4.2 Установить зависимости

```powershell
npm install
```

**Примечание**: Первая установка может занять 2-5 минут.

### 4.3 Запустить dev-сервер

```powershell
npm run dev
```

**Должно показать**:
```
  VITE v7.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

✅ **Frontend запущен на http://localhost:5173**

**Не закрывайте этот терминал!**

### 4.4 Открыть в браузере

Откройте http://localhost:5173

Должна загрузиться главная страница Standards Platform.

---

## Шаг 5 (Опционально): AI Backend (Django + DeepSeek)

Если хотите использовать **AI-помощника** на главной странице, запустите Django AI backend.

### 5.1 Получить DeepSeek API ключ

1. https://platform.deepseek.com/
2. Регистрация
3. API Keys → Create new key
4. Скопировать ключ (начинается с `sk-`)

### 5.2 Открыть ТРЕТИЙ PowerShell

```powershell
cd ~\Documents\building-standard-website\AI-ready-project\shnq_ai_backend
```

### 5.3 Создать виртуальное окружение

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 5.4 Установить зависимости

```powershell
# Основные Django зависимости
pip install django djangorestframework django-cors-headers python-dotenv

# OpenAI SDK (для DeepSeek)
pip install openai

# Admin панель
pip install -U django-jazzmin

# Sentence Transformers для embeddings (опционально, для RAG)
pip install sentence-transformers

# Qdrant client (опционально, для vector DB)
pip install qdrant-client
```

### 5.5 Настроить переменные окружения

```powershell
# Установить DeepSeek API ключ
$env:DEEPSEEK_API_KEY="sk-ваш-ключ-здесь"
$env:DEEPSEEK_BASE_URL="https://api.deepseek.com"

# Database URL (использует ту же PostgreSQL)
$env:DATABASE_URL="postgresql://postgres:ВАШ_ПАРОЛЬ@localhost:5432/standards_ai_db"
```

**⚠️ Замените**:
- `sk-ваш-ключ-здесь` на ваш DeepSeek API ключ
- `ВАШ_ПАРОЛЬ` на пароль PostgreSQL

### 5.6 Применить миграции

```powershell
python manage.py migrate
```

**Должно вывести**:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, ai_assistant
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

### 5.7 (Опционально) Создать суперпользователя Django

```powershell
python manage.py createsuperuser

# Email: admin@example.com
# Password: (введите пароль)
# Password (again): (повторите)
```

### 5.8 Запустить Django AI backend

```powershell
python manage.py runserver
```

**Должно показать**:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ **AI Backend запущен на http://localhost:8000**

**Не закрывайте этот терминал!**

### 5.9 Проверить работу AI

Откройте http://localhost:5173 (Frontend) и на главной странице должна появиться кнопка **🤖 AI-помощник**.

---

## ✅ Готово!

Теперь у вас запущено **3 сервиса**:

| Сервис | URL | Терминал |
|--------|-----|----------|
| Flask Backend | http://localhost:5000 | PowerShell #1 |
| React Frontend | http://localhost:5173 | PowerShell #2 |
| Django AI Backend | http://localhost:8000 | PowerShell #3 (опционально) |

**Тестовый администратор**:
- Email: `admin@standards.uz`
- Пароль: `admin123`

---

## 🛑 Остановка серверов

Нажмите **Ctrl+C** в каждом терминале чтобы остановить серверы.

**В следующий раз** для запуска:

```powershell
# Терминал 1: Backend
cd ~\Documents\building-standard-website\backend
.\venv\Scripts\Activate.ps1
python run.py

# Терминал 2: Frontend
cd ~\Documents\building-standard-website\frontend
npm run dev

# Терминал 3: AI Backend (опционально)
cd ~\Documents\building-standard-website\AI-ready-project\shnq_ai_backend
.\venv\Scripts\Activate.ps1
$env:DEEPSEEK_API_KEY="sk-ваш-ключ"
python manage.py runserver
```

---

## Troubleshooting

### ❌ Ошибка "execution policy"

**Проблема**:
```
.\venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled
```

**Решение**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### ❌ Flask не может подключиться к PostgreSQL

**Проблема**:
```
OperationalError: could not connect to server
```

**Проверьте**:

1. **PostgreSQL запущен**:
   - Win+R → `services.msc`
   - Найдите `postgresql-x64-15`
   - Status должен быть **Running**

2. **Правильный пароль в `.env`**:
   ```env
   DATABASE_URL=postgresql://postgres:ПРАВИЛЬНЫЙ_ПАРОЛЬ@localhost:5432/standards_db
   ```

3. **База данных создана**:
   ```powershell
   psql -U postgres
   \l  # Должна быть standards_db
   \q
   ```

---

### ❌ Frontend показывает "Failed to fetch"

**Проблема**: Frontend не может подключиться к Backend API.

**Проверьте**:

1. **Backend запущен** на http://localhost:5000
   ```powershell
   # В браузере откройте:
   http://localhost:5000/api/documents
   # Должно показать JSON с документами
   ```

2. **Правильный proxy в vite.config.js**:
   ```javascript
   // frontend/vite.config.js
   export default defineConfig({
     server: {
       proxy: {
         '/api': {
           target: 'http://localhost:5000',
           changeOrigin: true,
         },
       },
     },
   });
   ```

3. **CORS настроен в Backend**:
   ```python
   # backend/app/__init__.py
   CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
   ```

---

### ❌ AI-помощник не работает

**Проблема**: Кнопка AI не появляется или ошибка при запросе.

**Проверьте**:

1. **Django AI backend запущен** на http://localhost:8000
   ```powershell
   # В браузере откройте:
   http://localhost:8000/
   # Должна появиться страница Django
   ```

2. **DeepSeek API ключ установлен**:
   ```powershell
   # Проверьте переменную окружения
   echo $env:DEEPSEEK_API_KEY
   # Должно показать sk-...
   ```

3. **Backend проксирует запросы**:
   ```python
   # backend/app/routes/ai.py должен проксировать на http://localhost:8000
   AI_BACKEND_URL = os.getenv('AI_BACKEND_URL', 'http://localhost:8000')
   ```

---

### ❌ npm install завис или ошибки

**Решение**:

```powershell
# Очистите кеш
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force

# Установите снова
npm install
```

---

### ❌ Python package "wheel" ошибка

**Проблема**:
```
error: legacy-install-failure
```

**Решение**:
```powershell
pip install --upgrade pip setuptools wheel
pip install -r requirements-windows.txt
```

---

### ❌ "Port 5000 already in use"

**Проблема**: Порт 5000 уже занят.

**Решение 1** (найти и убить процесс):
```powershell
# Найти процесс на порту 5000
netstat -ano | findstr :5000

# Убить процесс (замените PID на номер из предыдущей команды)
taskkill /PID НОМЕР_PID /F
```

**Решение 2** (изменить порт Flask):
```python
# backend/run.py
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Изменено на 5001
```

Затем обновите `frontend/vite.config.js`:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5001',  // Изменено на 5001
    changeOrigin: true,
  },
}
```

---

### ❌ Docker Desktop не запускается

**Проблема**: "Docker Desktop failed to start"

**Решения**:

1. **Включить виртуализацию в BIOS**:
   - Перезагрузите компьютер
   - Войдите в BIOS (обычно F2/Del при загрузке)
   - Найдите "Virtualization Technology" или "Intel VT-x" / "AMD-V"
   - Включите (Enabled)
   - Сохраните и перезагрузитесь

2. **Включить WSL 2**:
   ```powershell
   # Запустите PowerShell от имени администратора
   wsl --install
   wsl --set-default-version 2
   ```

3. **Переустановить Docker Desktop**:
   - Удалите Docker Desktop через "Add or Remove Programs"
   - Скачайте последнюю версию: https://www.docker.com/products/docker-desktop/
   - Установите снова

---

### ❌ "no such file or directory: psql"

**Проблема**: Windows не может найти `psql.exe`.

**Решение 1** (добавить в PATH):
```powershell
# Найдите путь к PostgreSQL bin
# Обычно C:\Program Files\PostgreSQL\15\bin

# Добавьте в PATH:
$env:Path += ";C:\Program Files\PostgreSQL\15\bin"

# Проверьте:
psql --version
```

**Решение 2** (использовать полный путь):
```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

---

### ❌ Docker build очень медленный

**Проблема**: `docker-compose up --build` занимает 20+ минут.

**Решения**:

1. **Очистите Docker кеш**:
   ```powershell
   docker system prune -a
   ```

2. **Увеличьте ресурсы Docker Desktop**:
   - Docker Desktop → Settings → Resources
   - CPUs: минимум 4
   - Memory: минимум 4 GB
   - Swap: 1 GB

3. **Используйте WSL 2** вместо Hyper-V:
   - Docker Desktop → Settings → General
   - Включите "Use the WSL 2 based engine"

---

### ❌ Frontend пустая страница (white screen)

**Проблема**: http://localhost:5173 показывает пустую страницу.

**Проверьте в консоли браузера** (F12 → Console):

**Если ошибка "Failed to fetch module"**:
```powershell
cd frontend
rm -rf node_modules package-lock.json dist
npm install
npm run dev
```

**Если ошибка CORS**:
- Убедитесь что Backend запущен
- Проверьте что `FRONTEND_URL=http://localhost:5173` в `backend/.env`

---

### ❌ seed.py создает пустые документы

**Проблема**: После `python seed.py` в БД есть документы, но они не скачиваются.

**Причина**: Реальные PDF файлы находятся в Wasabi S3, seed.py создает только записи в БД.

**Решение**: Для тестирования используйте `bulk_upload.py` для загрузки реальных PDF:

```powershell
# В контейнере backend (Docker):
docker exec -it standards-backend bash
python /app/scripts/bulk_upload.py /path/to/pdfs --no-ai

# Или локально (без Docker):
cd backend
.\venv\Scripts\Activate.ps1
python scripts\bulk_upload.py C:\path\to\pdfs --no-ai
```

---

## 📞 Дополнительная помощь

Если проблема не решена:

1. **Проверьте логи**:
   ```powershell
   # Docker
   docker-compose logs -f backend
   
   # Локально
   # Смотрите вывод в терминале где запущен сервис
   ```

2. **Создайте issue** на GitHub с логами ошибки

3. **Документация**:
   - [CLAUDE.md](./CLAUDE.md) - полная техническая документация
   - [README.md](./README.md) - общий обзор
   - [DOCKER_README.md](./DOCKER_README.md) - Docker инструкции

---

**Последнее обновление**: 2026-05-02

**Версия**: 2.0.0
