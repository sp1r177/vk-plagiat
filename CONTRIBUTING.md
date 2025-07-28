# 🤝 Руководство по участию в проекте

Спасибо за интерес к проекту "Плагиат-Детектор"! Мы приветствуем любой вклад в развитие проекта.

## 🚀 Как начать

### 1. Форк репозитория
1. Перейдите на GitHub репозиторий
2. Нажмите кнопку "Fork" в правом верхнем углу
3. Склонируйте ваш форк локально

```bash
git clone https://github.com/YOUR_USERNAME/plagiarism-detector.git
cd plagiarism-detector
```

### 2. Настройка окружения

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 3. Настройка базы данных

```bash
# Создание БД
psql -U postgres -c "CREATE DATABASE plagiarism_detector;"

# Применение схемы
psql -U postgres -d plagiarism_detector -f ../database/schema.sql
```

### 4. Настройка переменных окружения

```bash
cp backend/env.example backend/.env
# Отредактируйте .env файл
```

## 📝 Процесс разработки

### 1. Создание ветки

```bash
git checkout -b feature/your-feature-name
# или
git checkout -b fix/your-bug-fix
```

### 2. Внесение изменений

- Следуйте стилю кода проекта
- Добавляйте комментарии к сложной логике
- Обновляйте документацию при необходимости

### 3. Тестирование

```bash
# Backend тесты
cd backend
python -m pytest tests/ -v

# Frontend тесты
cd frontend
npm test

# E2E тесты
npm run test:e2e
```

### 4. Коммит изменений

```bash
git add .
git commit -m "feat: add new feature description"
```

### 5. Push и Pull Request

```bash
git push origin feature/your-feature-name
```

Затем создайте Pull Request на GitHub.

## 📋 Стандарты кода

### Python (Backend)
- Используйте Black для форматирования
- Следуйте PEP 8
- Добавляйте типы (type hints)
- Покрывайте код тестами

```python
def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity using TF-IDF."""
    # Implementation
    pass
```

### JavaScript/React (Frontend)
- Используйте Prettier для форматирования
- Следуйте ESLint правилам
- Используйте функциональные компоненты
- Добавляйте PropTypes или TypeScript

```javascript
const PlagiarismCard = ({ similarity, originalUrl, plagiarizedUrl }) => {
  return (
    <Card>
      {/* Component content */}
    </Card>
  );
};
```

## 🧪 Тестирование

### Backend тесты
```bash
cd backend
python -m pytest tests/ -v --cov=.
```

### Frontend тесты
```bash
cd frontend
npm test -- --coverage
```

### Интеграционные тесты
```bash
docker-compose up -d
npm run test:integration
```

## 📚 Документация

### Обновление API документации
```bash
# Автоматическая генерация
cd backend
python -m uvicorn main:app --reload
# Откройте http://localhost:8000/docs
```

### Обновление README
- Обновляйте README.md при добавлении новых функций
- Добавляйте примеры использования
- Обновляйте скриншоты интерфейса

## 🐛 Сообщение об ошибках

При создании issue:

1. **Название**: Краткое описание проблемы
2. **Описание**: 
   - Шаги для воспроизведения
   - Ожидаемое поведение
   - Фактическое поведение
   - Версии ПО
   - Скриншоты (если применимо)

## 💡 Предложения новых функций

При создании feature request:

1. **Название**: Краткое описание функции
2. **Описание**:
   - Проблема, которую решает функция
   - Предлагаемое решение
   - Альтернативы (если есть)
   - Дополнительная информация

## 🏷 Семантические коммиты

Используйте префиксы для коммитов:

- `feat:` - новая функция
- `fix:` - исправление бага
- `docs:` - обновление документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг
- `test:` - добавление тестов
- `chore:` - обновление зависимостей

## 🚀 Быстрый старт для разработчиков

```bash
# Клонирование
git clone https://github.com/YOUR_USERNAME/plagiarism-detector.git
cd plagiarism-detector

# Запуск через Docker (рекомендуется)
docker-compose up -d

# Или локальный запуск
cd backend && python main.py
cd frontend && npm start
```

## 📞 Связь

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: [your-email@example.com]

## 🎯 Roadmap

- [ ] Поддержка других социальных сетей
- [ ] Улучшенные алгоритмы детекции
- [ ] Мобильное приложение
- [ ] API для внешних интеграций
- [ ] Машинное обучение для улучшения точности

Спасибо за ваш вклад! 🚀 