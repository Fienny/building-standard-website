# 🧪 Полный гайд по тестированию админки и автоматизации

## 📋 Что будем тестировать:

1. ✅ Flask Admin Panel (загрузка документов)
2. ✅ Автоматическая нормализация названий
3. ✅ Конвертация DOC/DOCX → PDF
4. ✅ Автоподсчёт страниц
5. ✅ Синхронизация с Django AI backend
6. ✅ Bulk upload скрипт (массовая загрузка)

---

## 🛠️ Подготовка окружения (Windows)

### 1. Установка LibreOffice

```powershell
# Скачай и установи LibreOffice:
# https://www.libreoffice.org/download/download/

# При установке:
# ✅ Поставь галочку "Add to PATH"

# Проверка установки:
libreoffice --version
# Должно вывести: LibreOffice 7.x.x.x
```

### 2. Подготовка архива документов

```powershell
# 1. Скачай UMUMIY.zip с Google Drive
# 2. Распакуй в папку проекта:

cd D:\benkas_projects\building-standard-website
mkdir documents-archive
# Распакуй UMUMIY.zip → documents-archive\UMUMIY\

# Должно быть:
# documents-archive\UMUMIY\
#   ├── shnk-1.02.07-19-uzb.rus.pdf
#   ├── SHNQ 1.02.10-23.doc
#   ├── КМҚ 1.03.04-22    ЯНГИ.pdf
#   └── ... (93 файла)
```

---

## 🚀 Запуск проекта (3 терминала)

### Терминал 1: Flask Backend

```powershell
cd D:\benkas_projects\building-standard-website\backend

# Активируй venv (если еще не активирован)
.\venv\Scripts\Activate.ps1

# Запусти Flask
python run.py

# Должно вывести:
# * Running on http://127.0.0.1:5000
```

### Терминал 2: Django AI Backend

```powershell
cd D:\benkas_projects\building-standard-website\AI-ready-project\shnq_ai_backend

# Активируй venv
.\venv\Scripts\Activate.ps1

# Установи зависимости (если еще не установлены)
pip install django djangorestframework django-cors-headers openai python-dotenv django-jazzmin

# Настрой DeepSeek API ключ
$env:DEEPSEEK_API_KEY="sk-your-api-key-here"
$env:DEEPSEEK_BASE_URL="https://api.deepseek.com"

# Примени миграции
python manage.py migrate

# Запусти Django
python manage.py runserver

# Должно вывести:
# Starting development server at http://127.0.0.1:8000/
```

### Терминал 3: React Frontend (опционально)

```powershell
cd D:\benkas_projects\building-standard-website\frontend

npm run dev

# Откроется: http://localhost:5173
```

---

## 🧪 Тест 1: Ручная загрузка через Admin Panel (API)

### Создай тестового админа

```powershell
# В терминале 1 (Flask backend с активированным venv):
cd backend
python

# В Python консоли:
>>> from app import create_app, db
>>> from app.models.user import User
>>> app = create_app()
>>> with app.app_context():
...     admin = User(email="test@admin.uz", name="Test Admin", role="admin")
...     admin.set_password("admin123")
...     db.session.add(admin)
...     db.session.commit()
...     print("✅ Админ создан")
...
>>> exit()
```

### Получи JWT токен

```powershell
# Через curl или Postman:
curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@admin.uz\",\"password\":\"admin123\"}'

# Ответ:
# {"access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."}

# Скопируй access_token - он понадобится дальше
```

### Загрузи документ через API

```powershell
# Подготовь тестовый файл:
# Возьми любой файл из documents-archive\UMUMIY\

# Загрузи через curl:
curl -X POST http://localhost:5000/api/admin/documents/new `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" `
  -F "file=@documents-archive\UMUMIY\shnk-1.02.07-19-uzb.rus.pdf" `
  -F "sync_ai=on"

# Должен вернуть:
# {
#   "status": "success",
#   "message": "Документ 'SHNQ 1.02.07-19' успешно добавлен (X стр.)",
#   "ai_sync": "success"
# }
```

### Проверь результат

```powershell
# 1. Проверь что документ появился в БД:
curl http://localhost:5000/api/documents | jq

# 2. Проверь что файл создан:
ls backend\uploads\documents\

# Должен быть: SHNQ_1.02.07-19.pdf

# 3. Проверь что документ появился в Django AI:
curl http://localhost:8000/api/chat/ `
  -H "Content-Type: application/json" `
  -d '{\"message\":\"SHNQ 1.02.07-19 haqida\"}'

# Если AI синхронизирован - вернёт ответ
```

---

## 🧪 Тест 2: Bulk Upload (массовая загрузка)

### Запусти скрипт

```powershell
cd D:\benkas_projects\building-standard-website\scripts

# Активируй venv backend:
..\backend\venv\Scripts\Activate.ps1

# Запусти bulk upload:
python bulk_upload.py ..\documents-archive\UMUMIY

# Должен вывести:
# 📂 Найдено файлов: 93
# 🤖 AI синхронизация: Вкл
# ============================================================
#
# [1/93] 🔄 2.01.04-18-pdf.pdf
#    ✅ SHNQ 2.01.04-18 (15 стр.)
#    🤖 AI синхронизирован
#
# [2/93] 🔄 kmk-2.01.03-19-uzbek-okonchatel...
#    ✅ KMQ 2.01.03-19 (28 стр.)
#    🤖 AI синхронизирован
#
# ... (все 93 файла)
#
# ============================================================
# 📊 ИТОГОВАЯ СТАТИСТИКА
# ============================================================
# Всего файлов:           93
# ✅ Успешно загружено:   90
# 📄 Конвертировано:      8
# 🤖 AI синхронизировано:  85
# ⚠️  AI ошибки:          5
# ❌ Ошибки обработки:    3
# ============================================================
#
# 📚 Всего документов в БД: 90
```

### Проверь результаты

```powershell
# 1. Сколько документов в Flask БД:
curl http://localhost:5000/api/documents | jq '. | length'
# Должно быть: ~90

# 2. Сколько файлов в папке:
ls backend\uploads\documents\ | Measure-Object
# Должно быть: ~90 PDF

# 3. Проверь что все нормализованы:
ls backend\uploads\documents\ | Select-String "SHNQ_|KMQ_|KR_"
# Все файлы должны быть в формате: SHNQ_X.XX.XX-YY.pdf

# 4. Проверь Django AI:
curl http://localhost:8000/admin/
# Должен открыться Django Admin (если не настроен - 404)
```

---

## 🧪 Тест 3: Автоматическая нормализация

### Тест на файле с плохим названием

```powershell
# Создай тестовый файл с плохим названием:
Copy-Item "documents-archive\UMUMIY\КМҚ 1.03.04-22    ЯНГИ.pdf" `
  -Destination "test-kmk-bad-name    spaces    .pdf"

# Загрузи через API:
curl -X POST http://localhost:5000/api/admin/documents/new `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -F "file=@test-kmk-bad-name    spaces    .pdf" `
  -F "sync_ai=on"

# Проверь что название нормализовалось:
ls backend\uploads\documents\KMQ_1.03.04-22.pdf

# Должен быть файл: KMQ_1.03.04-22.pdf (без пробелов!)
```

### Тест конвертации DOC → PDF

```powershell
# Возьми .doc или .docx файл:
curl -X POST http://localhost:5000/api/admin/documents/new `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -F "file=@documents-archive\UMUMIY\SHNQ 1.02.10-23.doc" `
  -F "sync_ai=on"

# Проверь что создался PDF:
ls backend\uploads\documents\SHNQ_1.02.10-23.pdf

# Оригинальный .doc должен быть удалён (конвертирован в PDF)
```

---

## 🧪 Тест 4: AI синхронизация

### Проверь что документ попал в AI

```powershell
# 1. Загрузи документ:
curl -X POST http://localhost:5000/api/admin/documents/new `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -F "file=@documents-archive\UMUMIY\shnk-1.02.07-19-uzb.rus.pdf" `
  -F "sync_ai=on"

# 2. Подожди 5 секунд (обработка)

# 3. Задай вопрос AI:
curl http://localhost:8000/api/chat/ `
  -H "Content-Type: application/json" `
  -d '{\"message\":\"SHNQ 1.02.07-19 nima haqida?\"}'

# Должен вернуть ответ с источниками:
# {
#   "answer": "...",
#   "sources": [{
#     "shnq_code": "SHNQ 1.02.07-19",
#     ...
#   }]
# }
```

### Проверь логи Django

```powershell
# В терминале 2 (Django) должны быть логи:
# sync_document: SHNQ 1.02.07-19 (15 pages)
# Document SHNQ 1.02.07-19 created successfully
```

---

## 🧪 Тест 5: Удаление документа

```powershell
# 1. Получи ID документа:
$doc_id = (curl http://localhost:5000/api/documents | jq '.[0].id')

# 2. Удали через API:
curl -X POST http://localhost:5000/api/admin/documents/$doc_id/delete `
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Проверь что удалился из БД:
curl http://localhost:5000/api/documents | jq '. | length'
# Должно уменьшиться на 1

# 4. Проверь что файл удалился:
ls backend\uploads\documents\
# Файл должен исчезнуть

# 5. Проверь что удалился из AI:
curl http://localhost:8000/api/chat/ `
  -d '{\"message\":\"<код удалённого документа>\"}'
# Не должно быть в sources
```

---

## 🧪 Тест 6: Проверка метаданных

```powershell
# Загрузи документ и проверь метаданные:
$response = curl -X POST http://localhost:5000/api/admin/documents/new `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -F "file=@documents-archive\UMUMIY\SHNQ 2.01.01-22.pdf" `
  -F "sync_ai=on" | ConvertFrom-Json

# Проверь что автоматически извлеклось:
curl http://localhost:5000/api/documents | jq '.[] | select(.code == "SHNQ 2.01.01-22")'

# Должно быть:
# {
#   "id": X,
#   "title": "SHNQ 2.01.01-22",
#   "category": "Строительство",
#   "year": 2022,
#   "pages": <автоподсчитано>,
#   "price": <pages * 1000>,
#   ...
# }
```

---

## ❌ Troubleshooting

### Ошибка: LibreOffice not found

```powershell
# Добавь LibreOffice в PATH:
$env:Path += ";C:\Program Files\LibreOffice\program"

# Или установи с галочкой "Add to PATH" и перезапусти PowerShell
```

### Ошибка: AI backend недоступен

```powershell
# Проверь что Django запущен:
curl http://localhost:8000/api/chat/
# Должен вернуть 400 (не Connection refused)

# Если Connection refused:
# 1. Запусти Django в терминале 2
# 2. Проверь что порт 8000 свободен: netstat -ano | findstr :8000
```

### Ошибка: Unauthorized (401)

```powershell
# JWT токен истёк (24 часа). Получи новый:
curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@admin.uz\",\"password\":\"admin123\"}'
```

### Документ загрузился но AI не синхронизировался

```powershell
# Проверь логи Django в терминале 2

# Ручная синхронизация:
curl -X POST http://localhost:5000/api/admin/documents/$doc_id/sync-ai `
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Чеклист успешного теста

- [ ] LibreOffice установлен и работает
- [ ] Flask backend запущен на :5000
- [ ] Django AI backend запущен на :8000
- [ ] Админ создан (test@admin.uz / admin123)
- [ ] JWT токен получен
- [ ] Ручная загрузка 1 документа через API - ✅
- [ ] Bulk upload 93 документов - ✅
- [ ] Все файлы нормализованы (SHNQ_X.XX.XX-YY.pdf)
- [ ] Конвертация DOC → PDF работает
- [ ] Автоподсчёт страниц работает
- [ ] AI синхронизация работает
- [ ] AI отвечает на вопросы по документам
- [ ] Удаление документа работает

---

## 🎯 Следующие шаги после тестирования:

1. **Если всё работает локально**:
   - Развернуть на сервере (Docker Compose)
   - Настроить production БД (PostgreSQL вместо SQLite для AI)
   - Настроить Nginx + SSL

2. **Если есть ошибки**:
   - Скинь мне логи из терминалов
   - Опиши что не работает
   - Я исправлю

3. **Дополнительные фичи**:
   - Web UI для админки (React компонент)
   - Bulk upload через UI (drag & drop)
   - Прогресс бар загрузки
   - Уведомления о статусе AI синхронизации
