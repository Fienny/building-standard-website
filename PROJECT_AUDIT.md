# 🔍 ПОЛНЫЙ АУДИТ ПРОЕКТА - Standards Platform

**Дата**: 2026-05-03  
**Версия**: 2.1.0

---

## 📊 ОБЩАЯ ГОТОВНОСТЬ

| Компонент | Готовность | Статус |
|-----------|------------|--------|
| Backend (Flask) | 80% | ✅ API работает, нет документов |
| AI Backend (Django) | 85% | ✅ RAG работает, нет auto-sync |
| Frontend (React) | 70% | ⚠️ UI готов, нет интеграции с AI |
| Infrastructure (Docker) | 90% | ✅ Все контейнеры работают |
| Security | 30% | 🔴 Критические уязвимости |
| Payments | 40% | 🔴 Код есть, не подключено |
| **ОБЩАЯ ГОТОВНОСТЬ** | **65%** | ⚠️ MVP возможен, production - нет |

---

## 🔴 ТОП-5 КРИТИЧЕСКИХ ПРОБЛЕМ

### 1️⃣ **НЕТ ДОКУМЕНТОВ В БАЗЕ**
**Проблема**: Backend и AI backend пустые  
**Решение**: Загрузить 154 документа из Wasabi  
**Код**:
```bash
docker compose exec backend python seed.py
# или
docker compose exec backend python scripts/bulk_upload.py /path/to/docs
```

### 2️⃣ **AI CHAT НЕ ПОКАЗЫВАЕТ РЕКОМЕНДАЦИИ**
**Проблема**: Home.jsx показывает ответ, но НЕ показывает "Купить документ"  
**Решение**: Доработать Home.jsx  
**Файл**: `frontend/src/pages/Home.jsx`

```jsx
{aiResponse && aiResponse.sources.length > 0 && (
  <div className="document-recommendation">
    <h3>📄 Рекомендуемый документ:</h3>
    <div className="doc-card">
      <p className="doc-code">{aiResponse.sources[0].shnq_code}</p>
      <p className="doc-price">Цена: {calculatePrice(aiResponse.sources[0])} сум</p>
      <button 
        className="btn btn-primary"
        onClick={() => handleBuyDocument(aiResponse.sources[0].shnq_code)}
      >
        💳 Купить документ
      </button>
    </div>
  </div>
)}
```

### 3️⃣ **НЕТ PROXY FLASK → DJANGO**
**Проблема**: Frontend обращается напрямую к :8000 (обходит auth!)  
**Решение**: Создать proxy endpoint в Flask  
**Файл**: `backend/app/routes/ai.py` (создать новый)

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import os

bp = Blueprint('ai', __name__, url_prefix='/api/ai')

AI_BACKEND_URL = os.getenv('AI_BACKEND_URL', 'http://ai-backend:8000')

@bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """Proxy AI chat запросов на Django backend"""
    user_id = get_jwt_identity()
    
    try:
        response = requests.post(
            f"{AI_BACKEND_URL}/api/chat/",
            json=request.json,
            timeout=60
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Зарегистрировать** в `backend/app/__init__.py`:
```python
from app.routes import ai
app.register_blueprint(ai.bp)
```

### 4️⃣ **НЕТ AUTO-SYNC FLASK → DJANGO**
**Проблема**: После загрузки PDF нужно вручную синхронизировать  
**Решение**: Вызывать sync_ai.py автоматически  
**Файл**: `backend/app/routes/documents.py`

```python
# После создания документа в Flask:
@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    # ... загрузка документа ...
    document = Document(...)
    db.session.add(document)
    db.session.commit()
    
    # AUTO-SYNC с AI backend
    try:
        from scripts.sync_ai import sync_document_to_ai
        sync_document_to_ai(document)
    except Exception as e:
        logger.error(f"AI sync failed: {e}")
    
    return jsonify(document.to_dict()), 201
```

### 5️⃣ **SECURITY - НЕТ HTTPS/RATE LIMITING**
**Проблема**: Сайт уязвим к атакам  
**Решение**:
1. **HTTPS**: nginx + certbot
2. **Rate Limiting**: Flask-Limiter

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # ...
```

---

## ⚠️ СРЕДНИЕ ПРОБЛЕМЫ (не критичные, но важные)

### 6. Frontend env variables хардкоден
**Файл**: `frontend/src/utils/api.js`  
**Сейчас**: `const API_BASE_URL = 'http://localhost:5000/api';`  
**Нужно**: `const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';`

### 7. Нет error handling в AI чате
- DeepSeek API упадет → белый экран
- Нет документов → непонятное сообщение

### 8. Нет auto-embeddings после создания Clause
**Решение**: Django signal

```python
# В app_shnq/models.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Clause)
def create_clause_embedding(sender, instance, created, **kwargs):
    if created:
        from .embeddings import upsert_clause_embeddings
        # Создать embedding только для нового clause
        # (можно оптимизировать через Celery queue)
        pass
```

### 9. Docker build медленный
- AI backend: 2GB torch/transformers каждый раз
- Frontend: npm install падает в Docker

**Решение**: Pre-built образы или Docker cache

### 10. Payment credentials отсутствуют
Click/PayMe код написан, но нужны реальные:
- `CLICK_MERCHANT_ID`
- `PAYME_MERCHANT_ID`
- Тестовые ключи

---

## 🟢 НИЗКИЙ ПРИОРИТЕТ

- Нет unit/integration тестов
- Нет CI/CD pipeline
- Нет централизованного logging
- Нет мониторинга (Prometheus/Grafana)
- i18n на фронтенде (все на русском)
- Dark mode
- Мобильная оптимизация

---

## 📋 ЧТО РАБОТАЕТ СЕЙЧАС

### ✅ Backend (Flask)
```bash
# Тест
curl http://localhost:5000/api/health
# {"status": "OK"}

curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@standards.uz","password":"admin123"}'
# {"access_token": "eyJ0..."}
```

### ✅ AI Backend (Django)
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Какая высота балкона?"}'
# {"answer":"...","sources":[...]}
```

### ✅ Frontend
- http://localhost → Главная с AI чатом
- http://localhost/login → Авторизация
- http://localhost/documents → Каталог
- http://localhost/profile → Личный кабинет

---

## 🎯 ПЛАН ДЕЙСТВИЙ (ПРИОРИТЕТЫ)

### 🔥 Фаза 1: КРИТИЧЕСКИЕ (3-5 дней)

**Задача 1**: Загрузить документы
```bash
# Проверить Wasabi доступ
docker compose exec backend python -c "from app.services.wasabi_service import list_documents; print(list_documents())"

# Загрузить
docker compose exec backend python seed.py
```

**Задача 2**: Создать `/api/ai/chat` proxy
- Создать `backend/app/routes/ai.py`
- Зарегистрировать blueprint
- Обновить `frontend/src/utils/api.js` → `/api/ai/chat`

**Задача 3**: Доработать Home.jsx
- Показывать рекомендацию документа
- Кнопка "Купить документ"
- Расчет цены

**Задача 4**: Auto-sync Flask → Django
- Вызывать `sync_ai.py` после upload
- Создавать embeddings автоматически

**Задача 5**: Протестировать полный флоу
```
1. Открыть сайт
2. Задать вопрос AI: "Какая высота балкона?"
3. Получить ответ + рекомендацию "SHNQ 3.01.02-23"
4. Увидеть цену: "45 000 сум"
5. Нажать "Купить документ"
6. → Payment flow
7. → Доступ к полному PDF
```

### ⚡ Фаза 2: ВАЖНЫЕ (1-2 недели)

**Задача 6**: Security
- HTTPS (certbot)
- Rate limiting
- Email verification
- Strong password policy

**Задача 7**: Payment интеграция
- Click тестовые credentials
- PayMe sandbox
- Тестирование callbacks

**Задача 8**: Error handling
- Try/catch во всех API calls
- Fallback UI при ошибках
- Logging

### 🌟 Фаза 3: УЛУЧШЕНИЯ (2-4 недели)

**Задача 9**: Оптимизация
- Docker pre-built images
- PostgreSQL connection pooling
- Frontend code splitting

**Задача 10**: Дополнительные фичи
- История чата
- Избранные документы
- Поиск с фильтрами
- Экспорт в Word/Excel

---

## 📁 ФАЙЛЫ ДЛЯ ИЗМЕНЕНИЯ

### Приоритет 1 (сейчас):
1. `backend/app/routes/ai.py` - создать proxy
2. `frontend/src/pages/Home.jsx` - доработать AI chat UI
3. `frontend/src/utils/api.js` - изменить AI_BACKEND_URL
4. `backend/app/routes/documents.py` - добавить auto-sync
5. `backend/seed.py` - проверить загрузку документов

### Приоритет 2 (потом):
6. `backend/app/__init__.py` - добавить Flask-Limiter
7. `AI-ready-project/shnq_ai_backend/app_shnq/models.py` - signals
8. `frontend/.env` - добавить VITE_API_URL
9. `docker-compose.yml` - оптимизация
10. `nginx.conf` - HTTPS настройка

---

## 💡 РЕКОМЕНДАЦИИ

### Для разработки:
1. **Сначала документы** - без них AI бесполезен
2. **Потом интеграция** - связать все части
3. **Потом security** - защитить
4. **Потом оптимизация** - ускорить

### Для production:
1. ⚠️ **НЕ ЗАПУСКАТЬ** без HTTPS
2. ⚠️ **НЕ ЗАПУСКАТЬ** без rate limiting
3. ⚠️ **НЕ ЗАПУСКАТЬ** без backup strategy
4. ✅ Использовать Gunicorn вместо Flask dev server
5. ✅ Настроить monitoring

### Для бизнеса:
1. **MVP готов** на 65%
2. **Неделя работы** → demo с реальными документами
3. **Месяц работы** → готов к первым пользователям
4. **Payments** можно подключить позже (сначала demo)

---

## 🎓 ЗАКЛЮЧЕНИЕ

### ✅ Что работает:
- Архитектура правильная
- Docker полностью настроен
- AI RAG система функциональна
- Frontend UI готов
- Backend API готово

### ❌ Что НЕ работает:
- Нет документов
- AI chat не интегрирован с покупкой
- Нет proxy Flask → Django
- Security минимальная
- Payments не подключены

### 🎯 Главная задача:
**ЗАГРУЗИТЬ 154 ДОКУМЕНТА И СВЯЗАТЬ ВСЕ ЧАСТИ**

После этого получим рабочий MVP для демо.

---

**Создано**: Claude Code  
**Дата**: 2026-05-03  
**Файл**: `PROJECT_AUDIT.md`
