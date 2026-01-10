# Руководство по развертыванию на QNAP NAS TS-433

## 📋 Содержание
1. [Подготовка QNAP](#подготовка-qnap)
2. [Установка Container Station](#установка-container-station)
3. [Создание структуры проекта](#создание-структуры-проекта)
4. [Настройка базы данных](#настройка-базы-данных)
5. [Развертывание backend](#развертывание-backend)
6. [Настройка Nginx](#настройка-nginx)
7. [Безопасность](#безопасность)
8. [Backup и мониторинг](#backup-и-мониторинг)

---

## 1. Подготовка QNAP

### 1.1. Первоначальная настройка

1. **Подключитесь к QNAP**
   - Откройте браузер и перейдите по IP адресу вашего QNAP
   - Например: `http://192.168.1.100` (IP может отличаться)
   - Войдите с учетными данными администратора

2. **Обновите QTS (операционную систему)**
   - Перейдите в `Control Panel` → `System` → `Firmware Update`
   - Установите последнюю версию QTS

3. **Создайте выделенное хранилище**
   - `Storage & Snapshots` → `Storage/Snapshots`
   - Создайте том для приложений (если еще не создан)
   - Рекомендуется выделить минимум 50-100 GB

### 1.2. Настройка сети

1. **Настройте статический IP** (рекомендуется)
   - `Control Panel` → `Network & File Services` → `Network`
   - Установите статический IP для стабильного доступа

2. **Откройте необходимые порты** в роутере:
   - `80` - HTTP
   - `443` - HTTPS
   - `22` - SSH (для администрирования)
   - Кастомные порты для backend API (например, `3000`)

---

## 2. Установка Container Station

### 2.1. Установка через App Center

1. Откройте `App Center` на QNAP
2. Найдите `Container Station`
3. Нажмите `Install`
4. Дождитесь завершения установки

### 2.2. Первый запуск Container Station

1. Откройте `Container Station`
2. При первом запуске будет выполнена инициализация
3. Ознакомьтесь с интерфейсом:
   - `Containers` - запущенные контейнеры
   - `Images` - образы Docker
   - `Applications` - приложения (docker-compose)
   - `Networks` - сети Docker
   - `Volumes` - тома для хранения данных

---

## 3. Создание структуры проекта

### 3.1. Подключение по SSH

```bash
# Подключитесь к QNAP по SSH
ssh admin@192.168.1.100
# Введите пароль администратора
```

### 3.2. Создание директорий

```bash
# Перейдите в общую папку
cd /share/Container

# Создайте структуру проекта
mkdir -p building-standards/{backend,database,nginx,ssl}
cd building-standards

# Создайте директории для данных
mkdir -p database/postgres-data
mkdir -p backend/uploads
mkdir -p backend/logs
mkdir -p nginx/conf
mkdir -p nginx/logs
```

### 3.3. Установка прав доступа

```bash
# Установите правильные права
chmod -R 755 /share/Container/building-standards
chown -R admin:administrators /share/Container/building-standards
```

---

## 4. Настройка базы данных

### 4.1. Выбор базы данных

Для проекта рекомендую **PostgreSQL**:
- Надежная и производительная
- Хорошо подходит для структурированных данных
- Отличная поддержка JSON
- Бесплатная и open-source

**Альтернатива**: MySQL/MariaDB

### 4.2. Создание docker-compose.yml для БД

Создайте файл `/share/Container/building-standards/docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: standards-db
    restart: always
    environment:
      POSTGRES_DB: standards_db
      POSTGRES_USER: standards_user
      POSTGRES_PASSWORD: ВАШ_СИЛЬНЫЙ_ПАРОЛЬ_ЗДЕСЬ
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=ru_RU.UTF-8"
    volumes:
      - ./database/postgres-data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - standards-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U standards_user -d standards_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis (для кэширования и сессий)
  redis:
    image: redis:7-alpine
    container_name: standards-redis
    restart: always
    command: redis-server --requirepass ВАШ_REDIS_ПАРОЛЬ
    volumes:
      - ./database/redis-data:/data
    ports:
      - "6379:6379"
    networks:
      - standards-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

networks:
  standards-network:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
```

### 4.3. Создание скрипта инициализации БД

Создайте файл `/share/Container/building-standards/database/init/01-init.sql`:

```sql
-- Создание таблиц для проекта

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица документов
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    category VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    pages INTEGER NOT NULL,
    price INTEGER NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    preview_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица покупок
CREATE TABLE IF NOT EXISTS purchases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    document_id INTEGER REFERENCES documents(id),
    amount INTEGER NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'pending',
    transaction_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица платежей
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    purchase_id INTEGER REFERENCES purchases(id),
    payment_system VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(255) UNIQUE,
    amount INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    payment_url TEXT,
    callback_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_purchases_user_id ON purchases(user_id);
CREATE INDEX idx_purchases_status ON purchases(payment_status);
CREATE INDEX idx_payments_transaction_id ON payments(transaction_id);
CREATE INDEX idx_payments_status ON payments(status);

-- Вставка тестовых данных
INSERT INTO documents (title, category, year, pages, price, description) VALUES
('ГОСТ 12.0.003-2015 ССБТ. Опасные и вредные производственные факторы', 'Безопасность труда', 2015, 15, 50000, 'Стандарт устанавливает классификацию опасных и вредных производственных факторов.'),
('ГОСТ 8.417-2002 Единицы величин', 'Метрология', 2002, 28, 45000, 'Настоящий стандарт устанавливает единицы физических величин, применяемые в Республике Узбекистан.'),
('ГОСТ 2.105-95 ЕСКД. Общие требования к текстовым документам', 'Документация', 1995, 32, 55000, 'Стандарт устанавливает общие требования к текстовым документам.'),
('ГОСТ 21.101-97 СПДС. Основные требования к проектной документации', 'Проектирование', 1997, 45, 75000, 'Стандарт устанавливает основные требования к проектной и рабочей документации.'),
('ГОСТ Р 57276-2016 Безопасность грузоподъемных кранов', 'Безопасность', 2016, 52, 85000, 'Стандарт устанавливает требования безопасности при эксплуатации грузоподъемных кранов.'),
('ГОСТ 34.602-89 Техническое задание. Требования к содержанию', 'ИТ и автоматизация', 1989, 18, 40000, 'Стандарт устанавливает требования к содержанию и оформлению технического задания.');
```

### 4.4. Запуск базы данных

```bash
cd /share/Container/building-standards

# Запустите контейнеры
docker-compose up -d

# Проверьте статус
docker-compose ps

# Просмотр логов
docker-compose logs -f postgres
```

---

## 5. Развертывание Backend

### 5.1. Создание структуры backend

Создайте структуру на вашем локальном компьютере:

```bash
cd building-standard-website
mkdir backend
cd backend
npm init -y
```

### 5.2. Установка зависимостей

```bash
npm install express cors dotenv pg pg-hstore sequelize bcrypt jsonwebtoken
npm install express-validator multer helmet compression morgan
npm install --save-dev nodemon
```

### 5.3. Основной файл backend (server.js)

Создайте файл `backend/server.js`:

```javascript
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
require('dotenv').config();

const app = express();

// Middleware
app.use(helmet());
app.use(compression());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('combined'));

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Импорт маршрутов
const authRoutes = require('./routes/auth');
const documentsRoutes = require('./routes/documents');
const paymentsRoutes = require('./routes/payments');

app.use('/api/auth', authRoutes);
app.use('/api/documents', documentsRoutes);
app.use('/api/payments', paymentsRoutes);

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Внутренняя ошибка сервера',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Backend server running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV}`);
});
```

### 5.4. Конфигурация окружения (.env)

Создайте файл `backend/.env`:

```env
# Server
NODE_ENV=production
PORT=3000
FRONTEND_URL=https://yoursite.uz

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=standards_db
DB_USER=standards_user
DB_PASSWORD=ВАШ_СИЛЬНЫЙ_ПАРОЛЬ_ЗДЕСЬ

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=ВАШ_REDIS_ПАРОЛЬ

# JWT
JWT_SECRET=ВАШ_ОЧЕНЬ_СЛОЖНЫЙ_СЕКРЕТНЫЙ_КЛЮЧ_МИНИМУМ_32_СИМВОЛА
JWT_EXPIRE=24h

# Payment Systems
CLICK_MERCHANT_ID=your_click_merchant_id
CLICK_SECRET_KEY=your_click_secret_key
PAYME_MERCHANT_ID=your_payme_merchant_id
PAYME_SECRET_KEY=your_payme_secret_key

# File Upload
MAX_FILE_SIZE=52428800
UPLOAD_PATH=/app/uploads
```

### 5.5. Dockerfile для backend

Создайте файл `backend/Dockerfile`:

```dockerfile
FROM node:18-alpine

# Установка рабочей директории
WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm ci --only=production

# Копирование исходного кода
COPY . .

# Создание пользователя без привилегий
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

USER nodejs

# Порт приложения
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Запуск приложения
CMD ["node", "server.js"]
```

### 5.6. Обновление docker-compose.yml

Добавьте backend в `docker-compose.yml`:

```yaml
  # Backend API
  backend:
    build: ./backend
    container_name: standards-backend
    restart: always
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/logs:/app/logs
    ports:
      - "3000:3000"
    depends_on:
      - postgres
      - redis
    networks:
      - standards-network
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 6. Настройка Nginx

### 6.1. Конфигурация Nginx

Создайте файл `/share/Container/building-standards/nginx/conf/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Логирование
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Оптимизация
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss;

    # Upstream для backend
    upstream backend {
        server backend:3000;
    }

    # HTTP сервер (редирект на HTTPS)
    server {
        listen 80;
        server_name yoursite.uz www.yoursite.uz;

        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS сервер
    server {
        listen 443 ssl http2;
        server_name yoursite.uz www.yoursite.uz;

        # SSL сертификаты (настроите позже)
        # ssl_certificate /etc/nginx/ssl/cert.pem;
        # ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Настройки SSL
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Frontend (статические файлы)
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;

            # Кеширование статических файлов
            location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;

            # Таймауты
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Ограничение размера загружаемых файлов
        client_max_body_size 50M;
    }
}
```

### 6.2. Добавление Nginx в docker-compose.yml

```yaml
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: standards-nginx
    restart: always
    volumes:
      - ./nginx/conf/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/logs:/var/log/nginx
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    networks:
      - standards-network
```

---

## 7. Безопасность

### 7.1. Firewall на QNAP

1. Откройте `Control Panel` → `Security` → `Security Level`
2. Включите `Enable Firewall`
3. Создайте правила:
   - Разрешить порт 80 (HTTP)
   - Разрешить порт 443 (HTTPS)
   - Разрешить порт 22 (SSH) только с вашего IP
   - Заблокировать все остальные входящие подключения

### 7.2. SSL сертификаты

**Вариант 1: Let's Encrypt (бесплатно)**

```bash
# Установите certbot в Container Station
docker run -it --rm \
  -v /share/Container/building-standards/nginx/ssl:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d yoursite.uz -d www.yoursite.uz \
  --email your@email.com --agree-tos
```

**Вариант 2: Через QNAP**
1. `Control Panel` → `System` → `Security` → `Certificate & Private Key`
2. Импортируйте или создайте сертификат

### 7.3. Регулярные обновления

```bash
# Создайте скрипт обновления контейнеров
cat > /share/Container/building-standards/update.sh << 'EOF'
#!/bin/bash
cd /share/Container/building-standards
docker-compose pull
docker-compose up -d
docker image prune -f
EOF

chmod +x /share/Container/building-standards/update.sh
```

---

## 8. Backup и мониторинг

### 8.1. Настройка автоматического backup

1. **Backup базы данных**

Создайте скрипт `/share/Container/building-standards/backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/share/Backups/building-standards"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec standards-db pg_dump -U standards_user standards_db | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Удалить бэкапы старше 30 дней
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_backup_$DATE.sql.gz"
```

2. **Настройка cron для автоматического backup**

```bash
# Откройте crontab
crontab -e

# Добавьте задачу (каждый день в 3:00)
0 3 * * * /share/Container/building-standards/backup-db.sh
```

### 8.2. Мониторинг через QNAP

1. Используйте встроенный `Resource Monitor` в QNAP
2. Установите `QTS Notifications` для получения уведомлений
3. Настройте email уведомления в `Control Panel` → `System` → `Notification`

### 8.3. Мониторинг контейнеров

```bash
# Проверка статуса всех контейнеров
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Проверка использования ресурсов
docker stats
```

---

## 9. Деплой и запуск

### 9.1. Финальный checklist

- [ ] QNAP обновлен до последней версии
- [ ] Container Station установлен
- [ ] Структура директорий создана
- [ ] docker-compose.yml настроен
- [ ] .env файлы созданы с правильными паролями
- [ ] SSL сертификаты получены
- [ ] Firewall настроен
- [ ] Backup скрипты созданы

### 9.2. Запуск всего стека

```bash
# Перейдите в директорию проекта
cd /share/Container/building-standards

# Соберите и запустите все контейнеры
docker-compose up -d --build

# Проверьте статус
docker-compose ps

# Проверьте логи
docker-compose logs -f

# Проверьте здоровье сервисов
curl http://localhost:3000/api/health
```

### 9.3. Проверка работоспособности

1. **Проверка БД:**
```bash
docker exec -it standards-db psql -U standards_user -d standards_db -c "SELECT count(*) FROM documents;"
```

2. **Проверка Backend:**
```bash
curl http://localhost:3000/api/health
```

3. **Проверка Nginx:**
```bash
curl http://localhost
```

---

## 10. Troubleshooting

### Частые проблемы:

**Контейнер не запускается:**
```bash
docker-compose logs <service-name>
```

**База данных не доступна:**
```bash
docker exec -it standards-db psql -U standards_user -d standards_db
```

**Недостаточно места:**
```bash
docker system prune -a
```

**Проблемы с сетью:**
```bash
docker network ls
docker network inspect standards-network
```

---

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs`
2. Проверьте статус: `docker-compose ps`
3. Проверьте документацию QNAP
4. Обратитесь к команде разработки

---

**Дата создания:** 2026-01-09
**Версия:** 1.0
