# Simple production Dockerfile - use pre-built dist

FROM nginx:alpine

# Копируем собранные файлы из локальной сборки
COPY dist /usr/share/nginx/html

# Копируем конфигурацию nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Порт
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
