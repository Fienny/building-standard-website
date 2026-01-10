FROM node:18-alpine

# Установка рабочей директории
WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm ci --only=production && \
    npm cache clean --force

# Копирование исходного кода
COPY . .

# Создание директорий для uploads и logs
RUN mkdir -p uploads logs && \
    chmod -R 755 uploads logs

# Создание пользователя без привилегий
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

# Переключение на непривилегированного пользователя
USER nodejs

# Порт приложения
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Запуск приложения
CMD ["node", "server.js"]
