# 🧪 Локальное тестирование с Wasabi и DeepSeek

## 📋 Что тестируем:

1. ✅ **Wasabi Storage** - загрузка документов в облако
2. ✅ **DeepSeek AI** - ответы на вопросы по документам
3. ✅ **Flask Backend** - обработка и нормализация
4. ✅ **Django AI Backend** - RAG, векторный поиск, переводы
5. ✅ **Bulk Upload** - массовая загрузка 93 документов

---

## 🛠️ Подготовка (Windows)

### 1. Установи зависимости

```powershell
# LibreOffice для конвертации DOC → PDF
# Скачай: https://www.libreoffice.org/download/
# ✅ При установке: "Add to PATH"

# Проверка:
libreoffice --version
```

### 2. Настрой окружение

**Backend .env:**
```powershell
cd backend
Copy-Item .env.example .env
notepad .env
```

Добавь в `backend/.env`:
```env
# Wasabi S3 Storage (уже есть в файле)
WASABI_ACCESS_KEY_ID=4E3G3COQYUP8GFKQHSNA
WASABI_SECRET_ACCESS_KEY=lPGcfRHzsDeDzvZu80EtfeqC5XMLn8eqlMVNySLm
WASABI_BUCKET_NAME=standards
WASABI_REGION=eu-central-1

# Остальное оставь по умолчанию
```

**AI Backend .env:**
```powershell
cd ..\AI-ready-project\shnq_ai_backend
Copy-Item .env.example .env
notepad .env
```

Добавь в `AI-ready-project/shnq_ai_backend/.env`:
```env
# DeepSeek API (уже есть в файле)
DEEPSEEK_API_KEY=sk-20296e85650049388631f75720e8b62f
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_CHAT_MODEL=deepseek-chat

# Остальное оставь по умолчанию
```

### 3. Установи Python зависимости

**Flask Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install boto3  # Для Wasabi
pip install -r requirements.txt
```

**Django AI Backend:**
```powershell
cd ..\AI-ready-project\shnq_ai_backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🚀 Запуск (3 терминала)

### Терминал 1: Flask Backend

```powershell
cd D:\benkas_projects\building-standard-website\backend
.\venv\Scripts\Activate.ps1

# Создай БД таблицы (первый раз):
python seed.py

# Запусти Flask:
python run.py

# ✅ Должно вывести: Running on http://127.0.0.1:5000
```

### Терминал 2: Django AI Backend

```powershell
cd D:\benkas_projects\building-standard-website\AI-ready-project\shnq_ai_backend
.\venv\Scripts\Activate.ps1

# Примени миграции (первый раз):
python manage.py migrate

# Запусти Django:
python manage.py runserver

# ✅ Должно вывести: Starting development server at http://127.0.0.1:8000/
```

### Терминал 3: Тесты

```powershell
cd D:\benkas_projects\building-standard-website\scripts
..\backend\venv\Scripts\Activate.ps1

# Готов к тестам!
```

---

## 🧪 ТЕСТ 1: Wasabi Storage

**Проверь подключение к Wasabi облаку:**

```powershell
# В терминале 3:
python test_wasabi.py
```

**Ожидаемый результат:**
```
🧪 ТЕСТ ПОДКЛЮЧЕНИЯ К WASABI STORAGE
============================================================

📋 Конфигурация:
   Bucket:  standards
   Region:  eu-central-1
   Access Key: 4E3G3COQYU...
   Secret Key: ********************

✅ Storage инициализирован

📤 Тест 1: Загрузка тестового файла...
   ✅ Файл загружен!
   URL: https://s3.eu-central-1.wasabisys.com/standards/test/test_file.txt

🔍 Тест 2: Проверка существования файла...
   ✅ Файл найден в bucket

🔗 Тест 3: Получение публичного URL...
   URL: https://s3.eu-central-1.wasabisys.com/standards/test/test_file.txt
   ✅ URL получен

📋 Тест 4: Список файлов в папке test/...
   Найдено файлов: 1
      - test/test_file.txt
   ✅ Список получен

🗑️  Тест 5: Удаление тестового файла...
   ✅ Файл удалён
   ✅ Подтверждено удаление

============================================================
✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!
============================================================

📌 Wasabi storage готов к использованию
```

**Если ошибка:**
- Проверь `backend/.env` - правильные ли credentials
- Проверь интернет - доступен ли `s3.eu-central-1.wasabisys.com`
- Проверь что bucket `standards` существует в Wasabi

---

## 🧪 ТЕСТ 2: DeepSeek AI

**Проверь что DeepSeek работает:**

```powershell
# В терминале 2 (Django) проверь логи при старте:
# Должно быть: "DeepSeek API initialized"

# Тестовый запрос к AI:
curl http://localhost:8000/api/chat/ `
  -H "Content-Type: application/json" `
  -d '{\"message\":\"test\",\"lang\":\"ru\"}'
```

**Ожидаемый результат:**
```json
{
  "answer": "Здравствуйте! Чем могу помочь?",
  "sources": [],
  "detected_lang": "ru"
}
```

**Если ошибка:**
- Проверь `AI-ready-project/shnq_ai_backend/.env` - правильный ли API ключ
- Проверь логи Django в терминале 2
- Проверь доступность `https://api.deepseek.com`

---

## 🧪 ТЕСТ 3: Загрузка документа в Wasabi

**Создай тестового админа:**

```powershell
# В терминале 1 (Flask):
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
>>> exit()
```

**Получи JWT токен:**

```powershell
curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@admin.uz\",\"password\":\"admin123\"}'

# Ответ:
# {"access_token": "eyJ0eXAiOiJKV1Qi..."}

# Скопируй токен в переменную:
$token = "eyJ0eXAiOiJKV1Qi..."
```

**Загрузи тестовый PDF:**

```powershell
# Создай тестовый PDF для проверки:
# Возьми любой PDF из архива UMUMIY или создай простой

curl -X POST http://localhost:5000/api/admin/documents/new `
  -H "Authorization: Bearer $token" `
  -F "file=@путь\к\test.pdf" `
  -F "sync_ai=on"
```

**Ожидаемый результат:**
```json
{
  "status": "success",
  "message": "Документ 'SHNQ X.XX.XX-YY' успешно добавлен (N стр.)",
  "ai_sync": "success"
}
```

**Проверь в Wasabi:**
- Открой https://console.wasabisys.com
- Зайди в bucket `standards`
- Папка `documents/`
- Там должен быть твой PDF: `SHNQ_X.XX.XX-YY.pdf`

**Проверь в БД:**
```powershell
curl http://localhost:5000/api/documents | jq
```

Должен быть документ с `file_path` = URL вида:
```
https://s3.eu-central-1.wasabisys.com/standards/documents/SHNQ_X.XX.XX-YY.pdf
```

---

## 🧪 ТЕСТ 4: Bulk Upload в Wasabi

**Подготовь архив документов:**

```powershell
# Скачай UMUMIY.zip с Google Drive
# Распакуй в:
D:\benkas_projects\building-standard-website\documents-archive\UMUMIY\

# Должно быть ~93 файла:
ls documents-archive\UMUMIY\ | Measure-Object
```

**Запусти массовую загрузку:**

```powershell
# В терминале 3:
python bulk_upload.py ..\documents-archive\UMUMIY
```

**Ожидаемый вывод:**
```
📂 Найдено файлов: 93
📁 Папка: D:\...\documents-archive\UMUMIY
🤖 AI синхронизация: Вкл
============================================================

[1/93] 🔄 shnk-1.02.07-19-uzb.rus.pdf
   ✅ SHNQ 1.02.07-19 (15 стр.)
   🤖 AI синхронизирован

[2/93] 🔄 SHNQ 1.02.10-23.doc
   ✅ SHNQ 1.02.10-23 (42 стр.)
   🤖 AI синхронизирован

[3/93] 🔄 КМҚ 1.03.04-22    ЯНГИ.pdf
   ✅ KMQ 1.03.04-22 (28 стр.)
   🤖 AI синхронизирован

... (все 93 файла)

============================================================
📊 ИТОГОВАЯ СТАТИСТИКА
============================================================
Всего файлов:           93
✅ Успешно загружено:   90
📄 Конвертировано:      8
🤖 AI синхронизировано:  85
⚠️  AI ошибки:          5
❌ Ошибки обработки:    3
============================================================

📚 Всего документов в БД: 90
```

**Процесс:**
1. Файл обрабатывается локально (нормализация, конвертация DOC→PDF)
2. Подсчитываются страницы
3. PDF загружается в Wasabi bucket `standards/documents/`
4. URL сохраняется в БД
5. Локальный temp файл удаляется
6. Документ синхронизируется с Django AI

**Проверь результат:**

```powershell
# Сколько документов в БД:
curl http://localhost:5000/api/documents | jq '. | length'
# Должно быть: ~90

# Проверь Wasabi Console:
# https://console.wasabisys.com → bucket standards → documents/
# Должно быть ~90 PDF файлов

# Локальная папка должна быть пустой (всё в Wasabi):
ls backend\uploads\documents\
# Должно быть пусто или только temp файлы
```

---

## 🧪 ТЕСТ 5: AI ответы по документам

**Задай вопрос по загруженному документу:**

```powershell
curl http://localhost:8000/api/chat/ `
  -H "Content-Type: application/json" `
  -d '{\"message\":\"SHNQ 1.02.07-19 nima haqida?\",\"lang\":\"uz\"}'
```

**Ожидаемый результат:**
```json
{
  "answer": "SHNQ 1.02.07-19 - это стандарт о...",
  "sources": [
    {
      "shnq_code": "SHNQ 1.02.07-19",
      "page": 1,
      "content": "...",
      "similarity": 0.85
    }
  ],
  "detected_lang": "uz",
  "translated": false
}
```

**Тест перевода Uzbek → Russian:**

```powershell
curl http://localhost:8000/api/chat/ `
  -H "Content-Type: application/json" `
  -d '{\"message\":\"Yer osti suvlarining sifati haqida qaysi standart?\",\"lang\":\"auto\"}'
```

**Ожидается:**
- Определит язык: `uz`
- Найдёт релевантный документ
- Переведёт ответ на русский (если настроено)

---

## 🧪 ТЕСТ 6: Удаление из Wasabi

**Удали документ:**

```powershell
# Получи ID документа:
$doc_id = (curl http://localhost:5000/api/documents | jq '.[0].id')

# Удали:
curl -X POST http://localhost:5000/api/admin/documents/$doc_id/delete `
  -H "Authorization: Bearer $token"
```

**Проверь:**
1. БД: документ удалён
2. Wasabi: файл удалён из bucket
3. Django AI: документ удалён из RAG базы

---

## ❌ Troubleshooting

### Ошибка: "boto3 not found"
```powershell
pip install boto3
```

### Ошибка: "Wasabi 403 Forbidden"
- Проверь credentials в `backend/.env`
- Проверь что bucket `standards` существует
- Проверь права доступа в Wasabi Console

### Ошибка: "DeepSeek API error"
- Проверь API ключ в `AI-ready-project/shnq_ai_backend/.env`
- Проверь баланс аккаунта DeepSeek
- Проверь логи Django в терминале 2

### Файл не загрузился в Wasabi
- Проверь логи Flask в терминале 1
- Проверь интернет подключение
- Попробуй запустить `test_wasabi.py` снова

### AI не синхронизировался
- Проверь что Django запущен (:8000)
- Проверь логи Django
- Ручная синхронизация:
```powershell
curl -X POST http://localhost:5000/api/admin/documents/$doc_id/sync-ai `
  -H "Authorization: Bearer $token"
```

---

## ✅ Чеклист успешного теста

- [ ] LibreOffice установлен
- [ ] `backend/.env` настроен (Wasabi credentials)
- [ ] `AI-ready-project/shnq_ai_backend/.env` настроен (DeepSeek key)
- [ ] boto3 установлен в Flask venv
- [ ] Flask запущен (:5000)
- [ ] Django запущен (:8000)
- [ ] Админ создан (test@admin.uz / admin123)
- [ ] **✅ ТЕСТ 1: Wasabi подключение** - test_wasabi.py прошёл
- [ ] **✅ ТЕСТ 2: DeepSeek AI** - ответил на тестовый вопрос
- [ ] **✅ ТЕСТ 3: Загрузка в Wasabi** - файл появился в bucket
- [ ] **✅ ТЕСТ 4: Bulk Upload** - 90+ документов загружены
- [ ] **✅ ТЕСТ 5: AI ответы** - находит документы и отвечает
- [ ] **✅ ТЕСТ 6: Удаление** - удаляется из Wasabi и AI

---

## 🎯 Что дальше:

### Если всё работает ✅:
1. Протестируй frontend (React на :5173)
2. Проверь интеграцию Flask ↔ React
3. Готовься к деплою на сервер

### Если есть проблемы ❌:
1. Скопируй логи из терминалов 1 и 2
2. Скриншот ошибки
3. Опиши что именно не работает
4. Скинь мне - поправлю

---

## 📝 Важные URL:

- Flask Backend: http://localhost:5000
- Django AI: http://localhost:8000
- React Frontend: http://localhost:5173
- Wasabi Console: https://console.wasabisys.com
- DeepSeek Dashboard: https://platform.deepseek.com

---

## 🔧 Полезные команды:

```powershell
# Проверить что Flask работает:
curl http://localhost:5000/api/documents

# Проверить что Django работает:
curl http://localhost:8000/api/chat/ -d '{\"message\":\"test\"}'

# Сбросить БД Flask:
cd backend
Remove-Item instance\standards.db
python seed.py

# Сбросить БД Django:
cd AI-ready-project\shnq_ai_backend
Remove-Item db.sqlite3
python manage.py migrate

# Посмотреть что в Wasabi:
# https://console.wasabisys.com → standards bucket

# Установить все зависимости заново:
cd backend
pip install -r requirements.txt
cd ..\AI-ready-project\shnq_ai_backend
pip install -r requirements.txt
```

---

**Удачи! 🚀**

Если что-то не работает - скриншоты + логи → мне в чат
