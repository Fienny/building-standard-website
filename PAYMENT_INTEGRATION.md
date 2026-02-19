# Интеграция платежных систем

Данное руководство описывает процесс интеграции платежных систем Click, PayMe и банковских карт (Uzcard/Humo) с платформой стандартов.

## Содержание

- [Обзор](#обзор)
- [Click](#click)
- [PayMe](#payme)
- [Банковские карты](#банковские-карты)
- [Тестирование](#тестирование)
- [Troubleshooting](#troubleshooting)

---

## Обзор

Платформа поддерживает три метода оплаты:

1. **Click** - популярная платежная система в Узбекистане
2. **PayMe** - платежная система от Payme
3. **Банковские карты** - Uzcard/Humo через агрегатор

### Архитектура

```
┌──────────┐         ┌──────────┐         ┌─────────────┐
│  Frontend│  POST   │  Backend │  API    │   Payment   │
│          ├────────►│  /api/   ├────────►│   Gateway   │
│          │         │ payments │         │ (Click/etc) │
└──────────┘         └────┬─────┘         └─────┬───────┘
                          │                     │
                          │   Webhook/Callback  │
                          │◄────────────────────┘
                          │
                          ▼
                    ┌──────────┐
                    │ Database │
                    │ (Update) │
                    └──────────┘
```

### Процесс оплаты

1. Пользователь выбирает документ и метод оплаты
2. Backend создает запись Purchase и Payment в БД
3. Backend обращается к API платежной системы для создания платежа
4. Пользователь перенаправляется на страницу оплаты платежной системы
5. После оплаты платежная система отправляет callback на наш сервер
6. Backend обрабатывает callback, обновляет статус платежа
7. Пользователь получает доступ к полной версии документа

---

## Click

### 1. Регистрация в Click

1. Зайдите на [Click Merchant](https://my.click.uz/)
2. Зарегистрируйтесь как мерчант
3. Создайте сервис и получите:
   - `CLICK_MERCHANT_ID`
   - `CLICK_SERVICE_ID`
   - `CLICK_SECRET_KEY`

### 2. Настройка конфигурации

Добавьте в `.env`:

```bash
CLICK_MERCHANT_ID=your_merchant_id
CLICK_SERVICE_ID=your_service_id
CLICK_SECRET_KEY=your_secret_key
```

### 3. Настройка webhook URL в Click

В личном кабинете Click укажите:

- **Prepare URL**: `https://yourdomain.uz/api/payments/callback/click`
- **Complete URL**: `https://yourdomain.uz/api/payments/callback/click`

### 4. Как работает Click

#### Создание платежа

```python
from app.services.click_service import ClickService

payment_data = ClickService.prepare_payment(
    amount=5000,  # в сумах
    merchant_trans_id="purchase_123",
    return_url="https://yourdomain.uz/payment/success",
    description="Покупка документа"
)

# Вернет: {payment_url, transaction_id, amount_tiyin}
```

#### Обработка callback

Click отправляет два запроса:

1. **Prepare** (action=0) - проверка возможности платежа
2. **Complete** (action=1) - подтверждение платежа

Backend автоматически обрабатывает оба запроса в `routes/payments.py:click_callback()`

#### Структура callback от Click

```python
{
    "click_trans_id": "12345",
    "service_id": "your_service_id",
    "merchant_trans_id": "purchase_123",
    "amount": "500000",  # в тийинах (1 сум = 100 тийин)
    "action": "1",  # 0 = prepare, 1 = complete
    "error": "0",
    "error_note": "Success",
    "sign_time": "2024-01-15 12:30:00",
    "sign_string": "hash_signature"
}
```

### 5. Тестирование Click

Click предоставляет тестовую среду:

- Тестовый URL: `https://my.click.uz/services/pay?service_id=...`
- Тестовые карты: указаны в документации Click

**Документация**: https://docs.click.uz/

---

## PayMe

### 1. Регистрация в PayMe

1. Зайдите на [PayMe Merchant](https://checkout.paycom.uz/)
2. Зарегистрируйтесь как мерчант
3. Получите:
   - `PAYME_MERCHANT_ID`
   - `PAYME_SECRET_KEY`

### 2. Настройка конфигурации

Добавьте в `.env`:

```bash
PAYME_MERCHANT_ID=your_merchant_id
PAYME_SECRET_KEY=your_secret_key
```

### 3. Настройка webhook URL в PayMe

В личном кабинете PayMe укажите:

- **Endpoint URL**: `https://yourdomain.uz/api/payments/callback/payme`
- **Test URL**: `https://yourdomain.uz/api/payments/callback/payme` (для тестирования)

### 4. Как работает PayMe

PayMe использует протокол **JSON-RPC 2.0**.

#### Создание платежа

```python
from app.services.payme_service import PaymeService

payment_data = PaymeService.prepare_payment(
    amount=5000,  # в сумах
    account_id="123",  # purchase_id
    description="Покупка документа",
    return_url="https://yourdomain.uz/payment/success"
)

# Вернет: {payment_url, encoded_params, amount_tiyin}
```

#### RPC методы

PayMe отправляет следующие JSON-RPC запросы:

1. **CheckPerformTransaction** - проверка возможности платежа
2. **CreateTransaction** - создание транзакции (резервирование средств)
3. **PerformTransaction** - выполнение транзакции (списание средств)
4. **CancelTransaction** - отмена транзакции
5. **CheckTransaction** - проверка статуса транзакции

Все методы обрабатываются в `routes/payments.py:payme_callback()`

#### Структура RPC запроса от PayMe

```json
{
  "method": "CheckPerformTransaction",
  "params": {
    "amount": 500000,
    "account": {
      "purchase_id": "123"
    }
  },
  "id": 1
}
```

#### Структура RPC ответа

```json
{
  "result": {
    "allow": true
  },
  "id": 1
}
```

### 5. Состояния транзакции PayMe

- `STATE_CREATED = 1` - создана
- `STATE_COMPLETED = 2` - завершена
- `STATE_CANCELLED = -1` - отменена
- `STATE_CANCELLED_AFTER_COMPLETE = -2` - отменена после завершения

### 6. Тестирование PayMe

- Тестовый merchant ID и ключ предоставляются при регистрации
- Используйте тестовые карты из документации PayMe

**Документация**: https://developer.help.paycom.uz/

---

## Банковские карты

Для приема платежей по картам Uzcard и Humo необходимо использовать агрегатор.

### Популярные агрегаторы в Узбекистане

1. **Apelsin** - https://apelsin.uz/
2. **Payze** - https://payze.io/
3. **Octo** - https://octo.uz/

### 1. Регистрация у агрегатора

Выберите агрегатора и зарегистрируйтесь. Получите:

- `CARD_MERCHANT_ID`
- `CARD_SECRET_KEY`
- `CARD_API_URL`

### 2. Настройка конфигурации

Добавьте в `.env`:

```bash
CARD_MERCHANT_ID=your_merchant_id
CARD_SECRET_KEY=your_secret_key
CARD_API_URL=https://api.your-aggregator.uz
```

### 3. Адаптация под конкретного агрегатора

Сервис `card_service.py` содержит **общую** реализацию. Вам нужно адаптировать его под API вашего агрегатора:

#### Для Apelsin

```python
# Пример интеграции с Apelsin
# Документация: https://docs.apelsin.uz/

payment_data = CardService.prepare_payment(
    amount=5000,
    order_id="purchase_123",
    description="Покупка документа",
    return_url="https://yourdomain.uz/payment/success",
    fail_url="https://yourdomain.uz/payment/failed"
)
```

#### Для Payze

```python
# Пример интеграции с Payze
# Документация: https://docs.payze.io/

# Обновите CardService в соответствии с API Payze
```

### 4. Обработка callback

Callback обрабатывается в `routes/payments.py:card_callback()`

Структура callback зависит от агрегатора. Общий формат:

```json
{
  "transaction_id": "txn_12345",
  "order_id": "purchase_123",
  "amount": 5000,
  "status": "success",
  "signature": "hash_signature"
}
```

### 5. Возврат средств (refund)

```python
from app.services.card_service import CardService

result = CardService.refund_payment(
    transaction_id="txn_12345",
    amount=5000  # опционально, для частичного возврата
)
```

---

## Тестирование

### Локальное тестирование webhook

Для локального тестирования webhook используйте ngrok:

```bash
# Установите ngrok
npm install -g ngrok

# Запустите туннель
ngrok http 5000

# Вы получите URL вида: https://abc123.ngrok.io
# Используйте его в настройках webhook платежных систем
```

### Тестовые данные

#### Click тестовые карты

Указаны в документации Click: https://docs.click.uz/test-cards/

#### PayMe тестовые карты

Указаны в документации PayMe: https://developer.help.paycom.uz/test-cards/

#### Тестовый сценарий

1. Создайте тестового пользователя
2. Выберите документ
3. Инициируйте оплату
4. Используйте тестовую карту
5. Проверьте, что статус платежа обновился в БД
6. Убедитесь, что пользователь получил доступ к документу

### Логирование

Для отладки добавьте логирование в callbacks:

```python
import logging

logger = logging.getLogger(__name__)

@payments_bp.route("/callback/click", methods=["POST"])
def click_callback():
    data = request.form.to_dict()
    logger.info(f"Click callback received: {data}")
    # ...
```

---

## Troubleshooting

### Click

**Проблема**: Получаю ошибку "Invalid signature"

**Решение**:
- Проверьте, что `CLICK_SECRET_KEY` правильный
- Убедитесь, что параметры для подписи отсортированы правильно
- Проверьте кодировку (должна быть UTF-8)

**Проблема**: Callback не приходит

**Решение**:
- Проверьте, что URL webhook доступен извне (используйте ngrok для локального тестирования)
- Убедитесь, что URL указан правильно в личном кабинете Click
- Проверьте логи сервера

### PayMe

**Проблема**: Получаю ошибку "Invalid amount"

**Решение**:
- PayMe ожидает сумму в **тийинах** (1 сум = 100 тийин)
- Умножьте сумму на 100: `amount_tiyin = amount * 100`

**Проблема**: JSON-RPC ошибка "Method not found"

**Решение**:
- Проверьте, что обрабатываете все необходимые методы RPC
- Убедитесь, что возвращаете правильный формат ответа

### Банковские карты

**Проблема**: Платеж не создается

**Решение**:
- Проверьте, что `CARD_API_URL` правильный
- Убедитесь, что адаптировали `CardService` под API вашего агрегатора
- Проверьте логи API запросов

**Проблема**: Callback signature invalid

**Решение**:
- Проверьте алгоритм генерации подписи (HMAC-SHA256 vs MD5 и т.д.)
- Убедитесь, что порядок параметров для подписи правильный
- Проверьте кодировку

---

## Полезные ссылки

- **Click**: https://docs.click.uz/
- **PayMe**: https://developer.help.paycom.uz/
- **Apelsin**: https://docs.apelsin.uz/
- **Payze**: https://docs.payze.io/
- **Octo**: https://octo.uz/

---

## Безопасность

### Важные правила

1. **Всегда проверяйте подпись** в callback
2. **Не доверяйте только callback** - используйте также проверку статуса через API
3. **Храните секретные ключи в переменных окружения**, не в коде
4. **Используйте HTTPS** для всех webhook URL
5. **Логируйте все транзакции** для аудита
6. **Используйте IP whitelist** если платежная система поддерживает

### Пример IP whitelist для nginx

```nginx
location /api/payments/callback/ {
    # Click IP addresses
    allow 185.178.51.0/24;

    # PayMe IP addresses
    allow 195.158.31.0/24;

    deny all;

    proxy_pass http://backend:5000;
}
```

---

## Следующие шаги

1. Зарегистрируйтесь в выбранных платежных системах
2. Получите API ключи и добавьте их в `.env`
3. Настройте webhook URL
4. Протестируйте с тестовыми картами
5. Проведите тестовые транзакции
6. Запустите в продакшн
7. Мониторьте логи и транзакции

---

## Поддержка

При возникновении проблем:

1. Проверьте логи backend: `docker-compose logs -f backend`
2. Проверьте документацию платежной системы
3. Свяжитесь с технической поддержкой платежной системы
4. Проверьте исходный код в `backend/app/services/` и `backend/app/routes/payments.py`
