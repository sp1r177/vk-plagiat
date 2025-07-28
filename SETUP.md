# 🚀 Быстрый запуск VK Mini App "Плагиат-Детектор"

## 📋 Что создано

Полнофункциональное VK Mini App для автоматического поиска плагиата контента в ВКонтакте с:

- ✅ **Backend**: FastAPI + PostgreSQL + VK API
- ✅ **Frontend**: React + VK Bridge SDK + VKUI
- ✅ **Мониторинг**: APScheduler (2 раза в день)
- ✅ **Детекция**: BM25/TF-IDF + imagehash
- ✅ **Уведомления**: VK Messages API
- ✅ **Биллинг**: VK Pay интеграция
- ✅ **Docker**: Полная контейнеризация

## 🏗 Структура проекта

```
plagiarism-detector/
├── backend/                 # FastAPI сервер
│   ├── main.py             # Точка входа
│   ├── config/             # Настройки
│   ├── models/             # Модели БД
│   ├── routers/            # API роутеры
│   ├── services/           # Бизнес-логика
│   ├── monitoring/         # Система мониторинга
│   ├── notifications/      # Уведомления
│   └── billing/           # Платежи
├── frontend/               # React приложение
│   ├── src/
│   │   ├── panels/        # Экраны приложения
│   │   ├── services/      # API клиенты
│   │   └── contexts/      # React контексты
│   └── public/
├── database/              # Схема БД
├── docs/                  # Документация
└── docker-compose.yml     # Docker развертывание
```

## ⚡ Быстрый старт

### 1. Клонирование и настройка

```bash
# Клонирование (если нужно)
git clone <repository-url>
cd plagiarism-detector

# Создание .env файла
cp backend/env.example backend/.env
# Отредактируйте backend/.env с вашими VK токенами
```

### 2. Запуск через Docker (рекомендуется)

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Логи
docker-compose logs -f backend
```

### 3. Ручной запуск

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (новый терминал)
cd frontend
npm install
npm start
```

## 🔧 Настройка VK

### 1. Создание VK App

1. Перейдите на https://vk.com/dev
2. Создайте новое приложение
3. Получите `VK_APP_ID` и `VK_APP_SECRET`

### 2. Получение токенов

```bash
# Access Token (для API)
curl "https://oauth.vk.com/access_token?client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&grant_type=client_credentials"

# Group Token (для уведомлений)
# Создайте группу и получите токен в настройках
```

### 3. Настройка VK Pay

1. Зарегистрируйтесь как мерчант
2. Получите `VK_PAY_MERCHANT_ID` и `VK_PAY_SECRET_KEY`

## 📱 Использование

### Основные функции:

1. **Добавление групп** - укажите ID группы ВКонтакте
2. **Автоматический мониторинг** - проверка 2 раза в день
3. **Уведомления** - получайте уведомления о плагиате
4. **История** - просматривайте найденные случаи
5. **Тарифы** - выбирайте подходящий план

### API эндпоинты:

- `GET /api/auth/me` - информация о пользователе
- `GET /api/groups/` - список групп
- `POST /api/groups/` - добавление группы
- `GET /api/monitoring/statistics` - статистика
- `GET /api/notifications/history` - история уведомлений
- `GET /api/billing/subscriptions` - тарифы

## 🎯 Тарифы

- **Бесплатно**: 1 группа на 1 день
- **Базовый**: 1 группа - 299₽/месяц
- **Стандарт**: 5 групп - 799₽/месяц
- **Премиум**: 10 групп - 1199₽/месяц

## 🔍 Алгоритм детекции

### Текст:
- Очистка от URL, хештегов, упоминаний
- Векторизация через TF-IDF
- Сравнение через косинусное расстояние

### Изображения:
- Загрузка и обработка через PIL
- Вычисление хеша через imagehash
- Сравнение расстояния Хэмминга

### Исключение репостов:
- Проверка `copy_history`
- Анализ ключевых слов
- Проверка attachments типа 'wall'

## 📊 Мониторинг

### Автоматический:
- 09:00 и 18:00 каждый день
- Проверка всех активных групп
- Отправка уведомлений при обнаружении

### Ручной:
- API: `POST /api/monitoring/start`
- Проверка отдельного поста: `POST /api/monitoring/check-post`

## 🛡 Безопасность

- JWT аутентификация
- Валидация VK Pay подписей
- Ограничение уведомлений (10/день)
- Проверка лимитов подписки

## 📈 Масштабирование

### Горизонтальное:
- Балансировщик нагрузки
- Redis для кеширования
- Очереди для задач

### Вертикальное:
- Увеличение воркеров
- Оптимизация БД запросов
- Добавление индексов

## 🐛 Отладка

```bash
# Логи backend
docker-compose logs backend

# Логи frontend
docker-compose logs frontend

# Подключение к БД
docker-compose exec postgres psql -U user -d plagiarism_detector

# Проверка API
curl http://localhost:8000/health
```

## 📚 Документация

- [API документация](docs/API.md)
- [Инструкция по развертыванию](docs/DEPLOYMENT.md)
- [Схема базы данных](database/schema.sql)

## 🎉 Готово!

Ваше VK Mini App готово к использованию! 

**Следующие шаги:**
1. Настройте VK токены в `.env`
2. Протестируйте API через Swagger UI
3. Запустите frontend и протестируйте интерфейс
4. Настройте продакшн развертывание

**Удачи в конкурсе VK Dev! 🚀** 