-- Создание базы данных
CREATE DATABASE plagiarism_detector;

-- Подключение к базе данных
\c plagiarism_detector;

-- Создание таблицы пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    vk_id INTEGER UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    photo_url TEXT,
    subscription_type VARCHAR(50) DEFAULT 'free',
    subscription_expires TIMESTAMP,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    max_groups INTEGER DEFAULT 1,
    total_plagiarism_found INTEGER DEFAULT 0,
    notifications_sent_today INTEGER DEFAULT 0,
    last_notification_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Создание таблицы групп
CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    vk_group_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    screen_name VARCHAR(255),
    photo_url TEXT,
    description TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    check_text BOOLEAN DEFAULT TRUE,
    check_images BOOLEAN DEFAULT TRUE,
    exclude_reposts BOOLEAN DEFAULT TRUE,
    posts_checked INTEGER DEFAULT 0,
    plagiarism_found INTEGER DEFAULT 0,
    last_check TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы случаев плагиата
CREATE TABLE plagiarism_cases (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    original_post_id VARCHAR(255) NOT NULL,
    original_group_id INTEGER NOT NULL,
    original_text TEXT,
    original_images JSONB,
    plagiarized_post_id VARCHAR(255) NOT NULL,
    plagiarized_group_id INTEGER NOT NULL,
    plagiarized_text TEXT,
    plagiarized_images JSONB,
    text_similarity FLOAT,
    image_similarity FLOAT,
    overall_similarity FLOAT NOT NULL,
    is_confirmed BOOLEAN DEFAULT FALSE,
    is_false_positive BOOLEAN DEFAULT FALSE,
    notification_sent BOOLEAN DEFAULT FALSE,
    notification_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации
CREATE INDEX idx_users_vk_id ON users(vk_id);
CREATE INDEX idx_groups_user_id ON groups(user_id);
CREATE INDEX idx_groups_vk_group_id ON groups(vk_group_id);
CREATE INDEX idx_plagiarism_group_id ON plagiarism_cases(group_id);
CREATE INDEX idx_plagiarism_created_at ON plagiarism_cases(created_at);
CREATE INDEX idx_plagiarism_overall_similarity ON plagiarism_cases(overall_similarity);

-- Создание представления для статистики
CREATE VIEW user_statistics AS
SELECT 
    u.id as user_id,
    u.vk_id,
    u.first_name,
    u.last_name,
    u.subscription_type,
    u.max_groups,
    COUNT(g.id) as active_groups,
    SUM(g.posts_checked) as total_posts_checked,
    SUM(g.plagiarism_found) as total_plagiarism_found,
    COUNT(pc.id) as plagiarism_cases_today
FROM users u
LEFT JOIN groups g ON u.id = g.user_id AND g.is_active = TRUE
LEFT JOIN plagiarism_cases pc ON g.id = pc.group_id AND pc.created_at >= CURRENT_DATE
WHERE u.is_active = TRUE
GROUP BY u.id, u.vk_id, u.first_name, u.last_name, u.subscription_type, u.max_groups;

-- Создание триггера для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_groups_updated_at BEFORE UPDATE ON groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plagiarism_cases_updated_at BEFORE UPDATE ON plagiarism_cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 