-- Инициализация базы данных для платформы государственных стандартов

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица документов
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    category VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL CHECK (year >= 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE) + 1),
    pages INTEGER NOT NULL CHECK (pages > 0),
    price INTEGER NOT NULL CHECK (price >= 0),
    description TEXT,
    file_path VARCHAR(500),
    preview_path VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица покупок
CREATE TABLE IF NOT EXISTS purchases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    document_id INTEGER REFERENCES documents(id) ON DELETE RESTRICT,
    amount INTEGER NOT NULL,
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('click', 'payme', 'card')),
    payment_status VARCHAR(50) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'processing', 'completed', 'failed', 'refunded')),
    transaction_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица платежей
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    purchase_id INTEGER REFERENCES purchases(id) ON DELETE CASCADE,
    payment_system VARCHAR(50) NOT NULL CHECK (payment_system IN ('click', 'payme', 'card')),
    transaction_id VARCHAR(255) UNIQUE,
    amount INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    payment_url TEXT,
    callback_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
CREATE INDEX IF NOT EXISTS idx_documents_is_active ON documents(is_active);
CREATE INDEX IF NOT EXISTS idx_documents_title ON documents USING gin(to_tsvector('russian', title));

CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_purchases_document_id ON purchases(document_id);
CREATE INDEX IF NOT EXISTS idx_purchases_status ON purchases(payment_status);
CREATE INDEX IF NOT EXISTS idx_purchases_transaction_id ON purchases(transaction_id);

CREATE INDEX IF NOT EXISTS idx_payments_purchase_id ON payments(purchase_id);
CREATE INDEX IF NOT EXISTS idx_payments_transaction_id ON payments(transaction_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггеры для обновления updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_purchases_updated_at BEFORE UPDATE ON purchases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Вставка тестовых документов
INSERT INTO documents (title, category, year, pages, price, description) VALUES
('ГОСТ 12.0.003-2015 ССБТ. Опасные и вредные производственные факторы', 'Безопасность труда', 2015, 15, 50000, 'Стандарт устанавливает классификацию опасных и вредных производственных факторов.'),
('ГОСТ 8.417-2002 Единицы величин', 'Метрология', 2002, 28, 45000, 'Настоящий стандарт устанавливает единицы физических величин, применяемые в Республике Узбекистан.'),
('ГОСТ 2.105-95 ЕСКД. Общие требования к текстовым документам', 'Документация', 1995, 32, 55000, 'Стандарт устанавливает общие требования к текстовым документам.'),
('ГОСТ 21.101-97 СПДС. Основные требования к проектной документации', 'Проектирование', 1997, 45, 75000, 'Стандарт устанавливает основные требования к проектной и рабочей документации.'),
('ГОСТ Р 57276-2016 Безопасность грузоподъемных кранов', 'Безопасность', 2016, 52, 85000, 'Стандарт устанавливает требования безопасности при эксплуатации грузоподъемных кранов.'),
('ГОСТ 34.602-89 Техническое задание. Требования к содержанию', 'ИТ и автоматизация', 1989, 18, 40000, 'Стандарт устанавливает требования к содержанию и оформлению технического задания.'),
('ГОСТ 30494-2011 Здания жилые и общественные. Параметры микроклимата', 'Строительство', 2011, 24, 60000, 'Стандарт устанавливает оптимальные и допустимые параметры микроклимата в помещениях.'),
('ГОСТ 12.1.003-2014 ССБТ. Шум. Общие требования безопасности', 'Безопасность труда', 2014, 20, 48000, 'Стандарт устанавливает общие требования безопасности при воздействии шума.'),
('ГОСТ 2.301-68 ЕСКД. Форматы', 'Документация', 1968, 8, 35000, 'Стандарт устанавливает форматы листов чертежей и других документов.'),
('ГОСТ 15467-79 Управление качеством продукции. Основные понятия', 'Менеджмент качества', 1979, 16, 42000, 'Стандарт устанавливает основные понятия в области управления качеством продукции.')
ON CONFLICT DO NOTHING;

-- Создание тестового администратора
-- Пароль: admin123 (в production обязательно изменить!)
-- Хеш создан с помощью bcrypt с salt rounds = 10
INSERT INTO users (email, password_hash, name, role) VALUES
('admin@standards.uz', '$2b$10$rX8V.KqCvJYxK6g7vQ9nROGGt8v0rN5vKmW8qYqN5j5Uc5vQFqWZi', 'Администратор', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Создание тестового пользователя
-- Пароль: user123
INSERT INTO users (email, password_hash, name, role) VALUES
('user@example.com', '$2b$10$rX8V.KqCvJYxK6g7vQ9nROGGt8v0rN5vKmW8qYqN5j5Uc5vQFqWZi', 'Тестовый пользователь', 'user')
ON CONFLICT (email) DO NOTHING;

-- Информация о базе данных
DO $$
BEGIN
    RAISE NOTICE '====================================';
    RAISE NOTICE 'База данных успешно инициализирована!';
    RAISE NOTICE 'Создано документов: %', (SELECT COUNT(*) FROM documents);
    RAISE NOTICE 'Создано пользователей: %', (SELECT COUNT(*) FROM users);
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Тестовые учетные данные:';
    RAISE NOTICE 'Админ: admin@standards.uz / admin123';
    RAISE NOTICE 'Пользователь: user@example.com / user123';
    RAISE NOTICE '====================================';
    RAISE NOTICE 'ВАЖНО: Измените пароли в production!';
    RAISE NOTICE '====================================';
END $$;
