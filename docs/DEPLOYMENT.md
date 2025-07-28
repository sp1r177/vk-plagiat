# Инструкция по развертыванию

## Требования

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- VK App (для получения токенов)

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd plagiarism-detector
```

### 2. Настройка Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Настройка базы данных

```bash
# Создание базы данных
psql -U postgres -c "CREATE DATABASE plagiarism_detector;"

# Применение схемы
psql -U postgres -d plagiarism_detector -f ../database/schema.sql
```

### 4. Настройка Frontend

```bash
cd ../frontend

# Установка зависимостей
npm install

# Создание .env файла
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
```

## Конфигурация

### Backend (.env)

```env
# База данных
DATABASE_URL=postgresql://user:password@localhost/plagiarism_detector

# VK API
VK_ACCESS_TOKEN=your_vk_access_token
VK_GROUP_TOKEN=your_vk_group_token
VK_APP_ID=your_vk_app_id
VK_APP_SECRET=your_vk_app_secret

# JWT
SECRET_KEY=your-secret-key-here-change-in-production

# Платежи
VK_PAY_MERCHANT_ID=your_vk_pay_merchant_id
VK_PAY_SECRET_KEY=your_vk_pay_secret_key

# Настройки приложения
DEBUG=True
```

### Получение VK токенов

1. Создайте приложение на https://vk.com/dev
2. Получите `VK_APP_ID` и `VK_APP_SECRET`
3. Получите `VK_ACCESS_TOKEN` через VK API
4. Создайте группу и получите `VK_GROUP_TOKEN`

### Настройка VK Pay

1. Зарегистрируйтесь как мерчант в VK Pay
2. Получите `VK_PAY_MERCHANT_ID` и `VK_PAY_SECRET_KEY`

## Запуск

### Development

```bash
# Backend
cd backend
python main.py

# Frontend (в новом терминале)
cd frontend
npm start
```

### Production

```bash
# Backend
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend
cd frontend
npm run build
# Разместите build/ папку на веб-сервере
```

## Docker

### Создание образов

```bash
# Backend
cd backend
docker build -t plagiarism-detector-backend .

# Frontend
cd ../frontend
docker build -t plagiarism-detector-frontend .
```

### Docker Compose

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: plagiarism_detector
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://user:password@postgres/plagiarism_detector
      VK_ACCESS_TOKEN: ${VK_ACCESS_TOKEN}
      VK_GROUP_TOKEN: ${VK_GROUP_TOKEN}
      VK_APP_ID: ${VK_APP_ID}
      VK_APP_SECRET: ${VK_APP_SECRET}
      SECRET_KEY: ${SECRET_KEY}
      VK_PAY_MERCHANT_ID: ${VK_PAY_MERCHANT_ID}
      VK_PAY_SECRET_KEY: ${VK_PAY_SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000/api

volumes:
  postgres_data:
```

## Мониторинг

### Логи

```bash
# Backend логи
tail -f backend/logs/app.log

# Мониторинг процессов
ps aux | grep python
ps aux | grep node
```

### База данных

```bash
# Подключение к БД
psql -U postgres -d plagiarism_detector

# Проверка таблиц
\dt

# Статистика
SELECT * FROM user_statistics;
```

## Безопасность

1. Измените `SECRET_KEY` в продакшене
2. Используйте HTTPS в продакшене
3. Настройте CORS для конкретных доменов
4. Ограничьте доступ к API по IP при необходимости
5. Регулярно обновляйте зависимости

## Масштабирование

### Горизонтальное масштабирование

1. Используйте балансировщик нагрузки
2. Настройте Redis для кеширования
3. Используйте очереди для обработки задач

### Вертикальное масштабирование

1. Увеличьте количество воркеров
2. Оптимизируйте запросы к БД
3. Добавьте индексы в БД

## Резервное копирование

```bash
# Бэкап базы данных
pg_dump -U postgres plagiarism_detector > backup.sql

# Восстановление
psql -U postgres plagiarism_detector < backup.sql
```

## Обновление

```bash
# Остановка сервисов
docker-compose down

# Обновление кода
git pull

# Пересборка образов
docker-compose build

# Запуск
docker-compose up -d
``` 