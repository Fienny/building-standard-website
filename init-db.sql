-- Инициализация баз данных для Standards Platform
-- standards_db уже создается через POSTGRES_DB

-- Подключаемся к стандартной БД и создаем расширения
\c standards_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Django AI Backend Database
CREATE DATABASE standards_ai_db;
\c standards_ai_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

