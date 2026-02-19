# Развертывание на DigitalOcean Droplet с подключением к QNAP NAS

Полное пошаговое руководство по развертыванию платформы государственных стандартов РУз.

## Архитектура

```
┌─────────────────────┐
│  DigitalOcean       │
│  Droplet            │
│  ┌───────────────┐  │
│  │ Nginx (80/443)│  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ Flask Backend │  │
│  │ (port 5000)   │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ PostgreSQL DB │  │
│  └───────────────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ NFS Mount     │◄─┼────── Интернет ──────┐
│  │ /mnt/qnap     │  │                       │
│  └───────────────┘  │                       │
└─────────────────────┘                       │
                                              │
                                              │
                                    ┌─────────▼──────────┐
                                    │  Офис (QNAP NAS)   │
                                    │  Статический IP    │
                                    │  ┌──────────────┐  │
                                    │  │ PDF/Word     │  │
                                    │  │ документы    │  │
                                    │  └──────────────┘  │
                                    │  NFS Server        │
                                    └────────────────────┘
```

---

## Часть 1: Подготовка QNAP NAS

### 1.1. Создание папки для документов

1. Войдите в веб-интерфейс QNAP (например, `http://QNAP_IP:8080`)
2. Откройте `Control Panel` → `Privilege` → `Shared Folders`
3. Нажмите `Create` → `Shared Folder`
   - **Folder Name**: `standards-documents`
   - **Disk Volume**: выберите том с достаточным местом
   - **Comment**: `PDF/Word файлы государственных стандартов`
4. Нажмите `Create`

### 1.2. Настройка прав доступа к папке

1. В списке shared folders выберите `standards-documents`
2. Нажмите `Edit Shared Folder Permissions`
3. Дайте права:
   - **admin**: Read/Write
   - Или создайте отдельного пользователя `standards_user` с правами Read/Write

### 1.3. Включение и настройка NFS

1. Откройте `Control Panel` → `Network & File Services` → `Win/Mac/NFS`
2. Перейдите на вкладку `NFS`
3. Поставьте галочку `Enable NFS service`
4. Нажмите `Apply`

### 1.4. Настройка NFS экспорта

1. В разделе `NFS` нажмите `Create` → `NFS Host Access`
2. Заполните форму:
   - **Shared folder**: выберите `standards-documents`
   - **Access right**: Read/Write
   - **Host/IP**: `DROPLET_IP` (IP вашего будущего Droplet)
   - **Squash**: `Map all users to admin` (или `No mapping`)
   - **Security**: `sys`
   - **Async**: оставьте включенным для производительности
3. Нажмите `Create`

### 1.5. Проверка настроек

Убедитесь, что:
- NFS сервис запущен
- Папка `standards-documents` доступна для экспорта
- В firewall QNAP разрешены порты NFS (2049, 111)

**Важно**: Запишите IP адрес QNAP. Например: `203.0.113.50`

---

## Часть 2: Создание и настройка DigitalOcean Droplet

### 2.1. Создание Droplet

1. Войдите в [DigitalOcean](https://cloud.digitalocean.com/)
2. Нажмите `Create` → `Droplets`
3. Выберите конфигурацию:
   - **Region**: ближайший к Узбекистану (например, Frankfurt, Amsterdam)
   - **Image**: Ubuntu 22.04 LTS
   - **Size**:
     - Минимум: Basic $6/mo (1 GB RAM, 1 vCPU, 25 GB SSD)
     - Рекомендуется: $12/mo (2 GB RAM, 1 vCPU, 50 GB SSD)
     - Для production: $24/mo (4 GB RAM, 2 vCPU, 80 GB SSD)
   - **Authentication**:
     - Создайте SSH ключ или используйте пароль
     - Рекомендуется SSH ключ для безопасности
   - **Hostname**: `standards-uz`
4. Нажмите `Create Droplet`

Дождитесь создания Droplet и запишите его IP адрес. Например: `159.65.123.45`

### 2.2. Первое подключение к Droplet

```bash
# Подключитесь по SSH
ssh root@DROPLET_IP

# Обновите систему
apt update && apt upgrade -y

# Установите базовые утилиты
apt install -y curl wget git vim htop
```

### 2.3. Создание пользователя (опционально, но рекомендуется)

```bash
# Создайте пользователя
adduser deploy

# Добавьте в группу sudo
usermod -aG sudo deploy

# Скопируйте SSH ключи (если используете)
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

Далее работайте от пользователя `deploy`:
```bash
su - deploy
```

### 2.4. Настройка firewall (UFW)

```bash
# Включите UFW
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Проверьте статус
sudo ufw status
```

### 2.5. Установка Docker и Docker Compose

```bash
# Установите зависимости
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Добавьте GPG ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавьте репозиторий Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установите Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Установите Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER

# Перелогиньтесь для применения изменений
exit
# Затем снова: ssh root@DROPLET_IP и su - deploy

# Проверьте установку
docker --version
docker-compose --version
```

---

## Часть 3: Монтирование QNAP через NFS

### 3.1. Установка NFS клиента

```bash
sudo apt update
sudo apt install -y nfs-common
```

### 3.2. Создание точки монтирования

```bash
# Создайте директорию
sudo mkdir -p /mnt/qnap-documents

# Установите права (временно, позже Docker будет использовать)
sudo chown -R $USER:$USER /mnt/qnap-documents
```

### 3.3. Тестовое монтирование

```bash
# Примонтируйте NFS share (замените QNAP_IP на реальный IP)
sudo mount -t nfs QNAP_IP:/standards-documents /mnt/qnap-documents

# Проверьте
ls -la /mnt/qnap-documents
df -h | grep qnap
```

Если команда `ls` показывает содержимое папки - всё работает!

### 3.4. Автоматическое монтирование при загрузке

Отредактируйте `/etc/fstab`:

```bash
sudo vim /etc/fstab
```

Добавьте в конец файла:

```
# QNAP NFS mount для документов
QNAP_IP:/standards-documents /mnt/qnap-documents nfs defaults,_netdev,rw 0 0
```

**Параметры:**
- `defaults` - стандартные опции монтирования
- `_netdev` - монтировать после поднятия сети
- `rw` - read-write доступ
- `0 0` - не делать fsck при загрузке

Протестируйте автомонтирование:

```bash
# Размонтируйте
sudo umount /mnt/qnap-documents

# Примонтируйте через fstab
sudo mount -a

# Проверьте
df -h | grep qnap
```

### 3.5. Проверка доступа

```bash
# Создайте тестовый файл
echo "Test from Droplet" | sudo tee /mnt/qnap-documents/test.txt

# Проверьте, что файл появился на QNAP
ls -la /mnt/qnap-documents/

# Удалите тест
sudo rm /mnt/qnap-documents/test.txt
```

---

## Часть 4: Деплой приложения

### 4.1. Клонирование репозитория

```bash
# Перейдите в домашнюю директорию
cd ~

# Клонируйте репозиторий
git clone YOUR_REPO_URL building-standard-website
cd building-standard-website
```

### 4.2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
vim .env
```

Содержимое:

```env
# Database
DB_PASSWORD=YOUR_STRONG_DB_PASSWORD_HERE

# Flask Backend
SECRET_KEY=YOUR_RANDOM_SECRET_KEY_32_CHARS_OR_MORE
JWT_SECRET_KEY=YOUR_RANDOM_JWT_SECRET_32_CHARS_OR_MORE

# Frontend URL (ваш домен)
FRONTEND_URL=https://standards.uz

# Price per page (1000 sum)
PRICE_PER_PAGE=1000
```

**Генерация секретных ключей:**

```bash
# Установите Python если нет
sudo apt install -y python3 python3-pip

# Сгенерируйте случайные ключи
python3 -c "import secrets; print(secrets.token_hex(32))"
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 4.3. Создание production docker-compose

Создайте файл `docker-compose.prod.yml`:

```bash
vim docker-compose.prod.yml
```

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
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - standards-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U standards_user -d standards_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Flask Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: standards-backend
    restart: always
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_URL=postgresql://standards_user:${DB_PASSWORD}@postgres:5432/standards_db
      - UPLOAD_FOLDER=/app/uploads/documents
      - PRICE_PER_PAGE=${PRICE_PER_PAGE:-1000}
      - FRONTEND_URL=${FRONTEND_URL}
    volumes:
      - /mnt/qnap-documents:/app/uploads/documents:ro
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - standards-network
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: standards-nginx
    restart: always
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
      - ./nginx/logs:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    networks:
      - standards-network

networks:
  standards-network:
    driver: bridge

volumes:
  postgres-data:
    driver: local
```

**Обратите внимание:**
- Backend монтирует `/mnt/qnap-documents` как **read-only** (`:ro`)
- Это безопаснее - backend может только читать файлы с QNAP

### 4.4. Настройка Nginx

Создайте директорию и конфиг:

```bash
mkdir -p nginx/ssl nginx/logs
vim nginx/nginx.conf
```

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
    client_max_body_size 100M;

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss application/pdf;

    # Upstream для backend
    upstream backend {
        server backend:5000;
    }

    # HTTP сервер (редирект на HTTPS)
    server {
        listen 80;
        server_name standards.uz www.standards.uz;

        # Для Let's Encrypt ACME challenge
        location /.well-known/acme-challenge/ {
            root /usr/share/nginx/html;
        }

        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS сервер
    server {
        listen 443 ssl http2;
        server_name standards.uz www.standards.uz;

        # SSL сертификаты (настроите позже)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Настройки SSL
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

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
    }
}
```

### 4.5. Сборка frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

### 4.6. Создание БД и начальные данные

```bash
# Запустите только PostgreSQL
docker-compose -f docker-compose.prod.yml up -d postgres

# Подождите пока БД запустится
sleep 10

# Запустите backend для инициализации
docker-compose -f docker-compose.prod.yml up -d backend

# Выполните seed скрипт
docker exec standards-backend python seed.py
```

Вы увидите:
```
+ Создан администратор: admin@standards.uz / admin123
+ Документ: ОзДСт 2710:2019 Строительство...
...
Готово! Seed завершен.
```

### 4.7. Запуск всех сервисов

```bash
# Запустите все контейнеры
docker-compose -f docker-compose.prod.yml up -d

# Проверьте статус
docker-compose -f docker-compose.prod.yml ps

# Проверьте логи
docker-compose -f docker-compose.prod.yml logs -f
```

Все сервисы должны быть `Up` и `healthy`.

---

## Часть 5: Настройка SSL сертификата (Let's Encrypt)

### 5.1. Установка Certbot

```bash
sudo apt update
sudo apt install -y certbot
```

### 5.2. Временно остановите Nginx

```bash
docker-compose -f docker-compose.prod.yml stop nginx
```

### 5.3. Получение сертификата

```bash
# Получите сертификат (замените на ваш домен)
sudo certbot certonly --standalone -d standards.uz -d www.standards.uz

# Введите email для уведомлений
# Согласитесь с условиями
```

Сертификаты будут сохранены в:
- `/etc/letsencrypt/live/standards.uz/fullchain.pem`
- `/etc/letsencrypt/live/standards.uz/privkey.pem`

### 5.4. Копирование сертификатов

```bash
# Скопируйте сертификаты в папку nginx
sudo cp /etc/letsencrypt/live/standards.uz/fullchain.pem ~/building-standard-website/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/standards.uz/privkey.pem ~/building-standard-website/nginx/ssl/key.pem

# Установите права
sudo chown $USER:$USER ~/building-standard-website/nginx/ssl/*.pem
chmod 644 ~/building-standard-website/nginx/ssl/cert.pem
chmod 600 ~/building-standard-website/nginx/ssl/key.pem
```

### 5.5. Автообновление сертификата

Создайте скрипт обновления:

```bash
sudo vim /usr/local/bin/renew-ssl.sh
```

```bash
#!/bin/bash
docker-compose -f /home/deploy/building-standard-website/docker-compose.prod.yml stop nginx
certbot renew --quiet
cp /etc/letsencrypt/live/standards.uz/fullchain.pem /home/deploy/building-standard-website/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/standards.uz/privkey.pem /home/deploy/building-standard-website/nginx/ssl/key.pem
docker-compose -f /home/deploy/building-standard-website/docker-compose.prod.yml start nginx
```

```bash
# Права на выполнение
sudo chmod +x /usr/local/bin/renew-ssl.sh

# Добавьте в crontab (обновление каждый месяц)
sudo crontab -e
```

Добавьте строку:
```
0 3 1 * * /usr/local/bin/renew-ssl.sh
```

### 5.6. Запустите Nginx

```bash
cd ~/building-standard-website
docker-compose -f docker-compose.prod.yml up -d nginx
```

---

## Часть 6: Настройка домена

### 6.1. DNS записи

В панели управления вашего регистратора доменов создайте A-записи:

| Тип | Имя | Значение | TTL |
|-----|-----|----------|-----|
| A | @ | DROPLET_IP | 3600 |
| A | www | DROPLET_IP | 3600 |

Подождите 15-30 минут для распространения DNS.

### 6.2. Проверка

```bash
# Проверьте DNS
dig standards.uz +short
dig www.standards.uz +short

# Должны вернуть IP вашего Droplet
```

### 6.3. Проверка сайта

Откройте в браузере:
- `http://standards.uz` → должен редиректить на `https://standards.uz`
- `https://standards.uz` → должен открыться сайт

---

## Часть 7: Загрузка документов на QNAP

### 7.1. Через веб-интерфейс QNAP

1. Откройте File Station в QNAP
2. Перейдите в `standards-documents`
3. Загрузите PDF файлы
4. Переименуйте файлы в понятные имена (например, `gost-12-0-003-2015.pdf`)

### 7.2. Через SCP/SFTP

```bash
# С вашего компьютера
scp document.pdf admin@QNAP_IP:/share/standards-documents/
```

### 7.3. Обновление БД

Подключитесь к БД и обновите `file_path`:

```bash
# Подключитесь к PostgreSQL контейнеру
docker exec -it standards-db psql -U standards_user -d standards_db

# Обновите file_path для документа
UPDATE documents SET file_path = 'gost-12-0-003-2015.pdf' WHERE id = 1;

# Выйдите
\q
```

Теперь документ будет доступен для предпросмотра и скачивания!

---

## Часть 8: Мониторинг и обслуживание

### 8.1. Просмотр логов

```bash
cd ~/building-standard-website

# Все логи
docker-compose -f docker-compose.prod.yml logs -f

# Только backend
docker-compose -f docker-compose.prod.yml logs -f backend

# Только nginx
docker-compose -f docker-compose.prod.yml logs -f nginx

# Только postgres
docker-compose -f docker-compose.prod.yml logs -f postgres
```

### 8.2. Проверка статуса контейнеров

```bash
docker-compose -f docker-compose.prod.yml ps

# Или
docker ps
```

### 8.3. Проверка использования ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Использование диска
df -h

# Использование NFS mount
df -h | grep qnap
```

### 8.4. Перезапуск сервисов

```bash
# Перезапуск всего стека
docker-compose -f docker-compose.prod.yml restart

# Перезапуск отдельного сервиса
docker-compose -f docker-compose.prod.yml restart backend
```

### 8.5. Обновление приложения

```bash
cd ~/building-standard-website

# Остановите контейнеры
docker-compose -f docker-compose.prod.yml down

# Получите последние изменения
git pull origin main

# Пересоберите frontend
cd frontend
npm install
npm run build
cd ..

# Пересоберите и запустите
docker-compose -f docker-compose.prod.yml up -d --build

# Проверьте логи
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Часть 9: Backup и восстановление

### 9.1. Backup базы данных

Создайте скрипт backup:

```bash
vim ~/backup-db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/backups"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec standards-db pg_dump -U standards_user standards_db | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Удалить бэкапы старше 30 дней
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/db_backup_$DATE.sql.gz"
```

```bash
chmod +x ~/backup-db.sh

# Добавьте в crontab (каждый день в 3:00)
crontab -e
```

Добавьте:
```
0 3 * * * /home/deploy/backup-db.sh
```

### 9.2. Восстановление из backup

```bash
# Распакуйте backup
gunzip db_backup_YYYYMMDD_HHMMSS.sql.gz

# Восстановите
cat db_backup_YYYYMMDD_HHMMSS.sql | docker exec -i standards-db psql -U standards_user -d standards_db
```

### 9.3. Копирование backup на удаленный сервер

```bash
# Отправка на другой сервер через SCP
scp ~/backups/db_backup_*.sql.gz user@backup-server:/backups/

# Или на S3 (если используете AWS)
# apt install awscli
# aws s3 cp ~/backups/ s3://your-bucket/backups/ --recursive
```

---

## Часть 10: Безопасность

### 10.1. Смена паролей по умолчанию

```bash
# Смените пароль администратора в БД
docker exec -it standards-db psql -U standards_user -d standards_db

# В psql:
UPDATE users SET password_hash = '$2b$10$NEW_HASH_HERE' WHERE email = 'admin@standards.uz';
\q
```

Или войдите на сайт и смените через интерфейс.

### 10.2. Ограничение SSH доступа

Отредактируйте `/etc/ssh/sshd_config`:

```bash
sudo vim /etc/ssh/sshd_config
```

Измените:
```
PermitRootLogin no
PasswordAuthentication no  # Только SSH ключи
```

Перезапустите SSH:
```bash
sudo systemctl restart sshd
```

### 10.3. Fail2ban для защиты от брутфорса

```bash
sudo apt install -y fail2ban

# Запустите и включите автозапуск
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 10.4. Автоматические обновления безопасности

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## Troubleshooting

### Проблема: NFS mount не работает

**Решение:**
```bash
# Проверьте доступность QNAP
ping QNAP_IP

# Проверьте, что NFS сервис запущен на QNAP
showmount -e QNAP_IP

# Проверьте логи
sudo journalctl -u rpc-statd
dmesg | grep nfs
```

### Проблема: Backend не может прочитать файлы с QNAP

**Решение:**
```bash
# Проверьте права на mount point
ls -la /mnt/qnap-documents

# Проверьте, что backend видит файлы
docker exec standards-backend ls -la /app/uploads/documents

# Проверьте логи backend
docker-compose -f docker-compose.prod.yml logs backend
```

### Проблема: SSL сертификат не работает

**Решение:**
```bash
# Проверьте сертификаты
sudo certbot certificates

# Проверьте файлы в nginx
ls -la ~/building-standard-website/nginx/ssl/

# Перезапустите nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Проблема: Сайт недоступен

**Решение:**
```bash
# Проверьте статус контейнеров
docker ps

# Проверьте порты
sudo netstat -tulpn | grep -E ':(80|443)'

# Проверьте firewall
sudo ufw status

# Проверьте логи nginx
docker-compose -f docker-compose.prod.yml logs nginx
```

### Проблема: База данных не запускается

**Решение:**
```bash
# Проверьте логи
docker-compose -f docker-compose.prod.yml logs postgres

# Проверьте место на диске
df -h

# Пересоздайте контейнер
docker-compose -f docker-compose.prod.yml down
docker volume rm building-standard-website_postgres-data
docker-compose -f docker-compose.prod.yml up -d postgres
```

---

## Полезные команды

### Системная информация

```bash
# Использование CPU и RAM
htop

# Использование диска
df -h

# Использование сети
iftop

# Процессы Docker
docker ps
docker stats
```

### Управление Docker

```bash
# Остановить все контейнеры
docker-compose -f docker-compose.prod.yml down

# Пересобрать контейнеры
docker-compose -f docker-compose.prod.yml build

# Удалить неиспользуемые образы и volumes
docker system prune -a
```

### Работа с БД

```bash
# Подключиться к PostgreSQL
docker exec -it standards-db psql -U standards_user -d standards_db

# Экспортировать данные
docker exec standards-db pg_dump -U standards_user standards_db > dump.sql

# Импортировать данные
cat dump.sql | docker exec -i standards-db psql -U standards_user -d standards_db
```

---

## Checklist развертывания

- [ ] QNAP настроен и доступен по статическому IP
- [ ] NFS экспорт настроен на QNAP
- [ ] Droplet создан на DigitalOcean
- [ ] Docker и Docker Compose установлены
- [ ] NFS клиент установлен и работает
- [ ] QNAP успешно примонтирован через NFS
- [ ] Репозиторий склонирован
- [ ] .env файл создан с правильными переменными
- [ ] Frontend собран (npm run build)
- [ ] База данных инициализирована (seed.py)
- [ ] Все контейнеры запущены и healthy
- [ ] SSL сертификат получен и настроен
- [ ] DNS записи настроены
- [ ] Сайт открывается по домену
- [ ] PDF файлы загружены на QNAP
- [ ] Документы доступны для предпросмотра
- [ ] Backup скрипт настроен
- [ ] Мониторинг настроен

---

## Контакты и поддержка

При возникновении проблем:
1. Проверьте раздел Troubleshooting
2. Посмотрите логи: `docker-compose logs`
3. Проверьте статус сервисов: `docker-compose ps`

**Важные файлы:**
- Логи Nginx: `~/building-standard-website/nginx/logs/`
- Логи backend: `docker-compose logs backend`
- Логи PostgreSQL: `docker-compose logs postgres`

---

**Версия документа:** 1.0
**Последнее обновление:** 2026-02-19
