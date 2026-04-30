-- Инициализация баз данных для Standards Platform
-- Создается две БД: для Flask backend и для Django AI backend

-- Flask Backend Database
CREATE DATABASE standards_db;
\c standards_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Django AI Backend Database
CREATE DATABASE standards_ai_db;
\c standards_ai_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;  -- для pgvector если будем использовать

-- Возвращаемся к дефолтной БД
\c postgres;
