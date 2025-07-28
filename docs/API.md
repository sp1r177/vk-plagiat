# API Документация - Плагиат-Детектор

## Базовый URL
```
http://localhost:8000/api
```

## Аутентификация

Все запросы (кроме авторизации) требуют JWT токен в заголовке:
```
Authorization: Bearer <token>
```

## Эндпоинты

### Аутентификация

#### POST /auth/vk-login
Авторизация через VK

**Параметры:**
```json
{
  "vk_id": 123456789
}
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Получение информации о текущем пользователе

**Ответ:**
```json
{
  "id": 1,
  "vk_id": 123456789,
  "first_name": "Иван",
  "last_name": "Иванов",
  "photo_url": "https://vk.com/images/camera_200.png",
  "subscription_type": "basic",
  "subscription_expires": "2024-02-15T00:00:00Z",
  "notifications_enabled": true,
  "max_groups": 1,
  "total_plagiarism_found": 5,
  "notifications_sent_today": 2,
  "last_notification_date": "2024-01-15T10:30:00Z"
}
```

### Группы

#### GET /groups/
Получение списка групп пользователя

**Ответ:**
```json
[
  {
    "id": 1,
    "vk_group_id": 123456,
    "name": "Тестовая группа",
    "screen_name": "test_group",
    "photo_url": "https://vk.com/images/group_200.png",
    "description": "Описание группы",
    "user_id": 1,
    "is_active": true,
    "check_text": true,
    "check_images": true,
    "exclude_reposts": true,
    "posts_checked": 150,
    "plagiarism_found": 3,
    "last_check": "2024-01-15T09:00:00Z"
  }
]
```

#### POST /groups/
Добавление новой группы

**Параметры:**
```json
{
  "vk_group_id": 123456,
  "check_text": true,
  "check_images": true,
  "exclude_reposts": true
}
```

#### PUT /groups/{group_id}
Обновление настроек группы

**Параметры:**
```json
{
  "check_text": false,
  "check_images": true,
  "exclude_reposts": true
}
```

#### DELETE /groups/{group_id}
Удаление группы из мониторинга

### Мониторинг

#### GET /monitoring/statistics
Получение статистики мониторинга

**Ответ:**
```json
{
  "total_groups": 3,
  "total_posts_checked": 450,
  "total_plagiarism_found": 12,
  "average_plagiarism_rate": 2.67,
  "daily_statistics": [
    {
      "date": "2024-01-15",
      "plagiarism_found": 2
    }
  ]
}
```

#### POST /monitoring/start
Запуск мониторинга вручную

#### GET /monitoring/status
Получение статуса мониторинга

#### POST /monitoring/check-post
Проверка отдельного поста

**Параметры:**
```json
{
  "post_url": "https://vk.com/wall-123456_789"
}
```

### Уведомления

#### GET /notifications/history
Получение истории уведомлений

**Параметры:**
- `limit` (int, опционально): количество записей (по умолчанию 20)
- `offset` (int, опционально): смещение (по умолчанию 0)

**Ответ:**
```json
{
  "history": [
    {
      "id": 1,
      "created_at": "2024-01-15T10:30:00Z",
      "overall_similarity": 0.85,
      "text_similarity": 0.90,
      "image_similarity": 0.75,
      "original_post_url": "https://vk.com/wall-123456_789",
      "plagiarized_post_url": "https://vk.com/wall-654321_987",
      "group_name": "Тестовая группа"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### GET /notifications/statistics
Получение статистики уведомлений

**Ответ:**
```json
{
  "today": 2,
  "week": 8,
  "month": 25,
  "total": 42,
  "notifications_sent_today": 2,
  "max_notifications_per_day": 10
}
```

#### PUT /notifications/settings
Обновление настроек уведомлений

**Параметры:**
```json
{
  "notifications_enabled": true
}
```

### Биллинг

#### GET /billing/subscriptions
Получение списка доступных подписок

**Ответ:**
```json
{
  "subscriptions": [
    {
      "type": "free",
      "name": "Бесплатно",
      "groups": 1,
      "days": 1,
      "price": 0,
      "price_kop": 0
    },
    {
      "type": "basic",
      "name": "Базовый",
      "groups": 1,
      "days": 30,
      "price": 299,
      "price_kop": 29900
    }
  ]
}
```

#### POST /billing/create-payment
Создание платежа

**Параметры:**
```json
{
  "subscription_type": "basic"
}
```

#### GET /billing/my-subscription
Получение информации о текущей подписке

**Ответ:**
```json
{
  "subscription_type": "basic",
  "subscription_name": "Базовый",
  "max_groups": 1,
  "expires_at": "2024-02-15T00:00:00Z",
  "is_active": true,
  "days_left": 30
}
```

## Коды ошибок

- `400 Bad Request` - Неверные параметры запроса
- `401 Unauthorized` - Не авторизован
- `403 Forbidden` - Нет доступа
- `404 Not Found` - Ресурс не найден
- `429 Too Many Requests` - Превышен лимит запросов
- `500 Internal Server Error` - Внутренняя ошибка сервера

## Лимиты

- Максимум 10 уведомлений в день
- Мониторинг 2 раза в день (09:00 и 18:00)
- Лимит групп зависит от тарифа 