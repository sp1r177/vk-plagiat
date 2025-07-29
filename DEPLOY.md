# Деплой проекта на GitHub Pages

## Быстрый старт

### 1. Подготовка репозитория

1. Создайте новый репозиторий на GitHub
2. Клонируйте его локально:
```bash
git clone https://github.com/your-username/vk-plagiat.git
cd vk-plagiat
```

### 2. Настройка GitHub Pages

1. Перейдите в Settings репозитория
2. Найдите раздел "Pages"
3. В "Source" выберите "GitHub Actions"
4. Сохраните настройки

### 3. Обновление homepage в package.json

Замените `your-username` на ваше имя пользователя GitHub:

```json
{
  "homepage": "https://your-username.github.io/vk-plagiat"
}
```

### 4. Пуш в репозиторий

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 5. Проверка деплоя

1. Перейдите в Actions вкладку репозитория
2. Дождитесь завершения workflow "Deploy to GitHub Pages"
3. Перейдите по ссылке: `https://your-username.github.io/vk-plagiat`

## Локальная разработка

### Запуск frontend

```bash
cd frontend
npm install
npm start
```

Приложение будет доступно по адресу: http://localhost:3000

### Запуск backend (опционально)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend будет доступен по адресу: http://localhost:8000

## Структура деплоя

- **GitHub Pages**: Только frontend часть (React приложение)
- **Демо режим**: Приложение работает без backend, используя моковые данные
- **VK интеграция**: Полная функциональность доступна только в VK Mini App

## Проверка работоспособности

1. **Демо режим**: Приложение загружается с тестовыми данными
2. **Навигация**: Все панели доступны для просмотра
3. **UI**: VKUI компоненты отображаются корректно
4. **Адаптивность**: Приложение адаптируется под разные размеры экрана

## Устранение проблем

### Ошибка 404 на GitHub Pages
- Убедитесь, что в package.json указан правильный homepage
- Проверьте, что ветка называется `main`

### Приложение не загружается
- Проверьте консоль браузера на ошибки
- Убедитесь, что все зависимости установлены

### Проблемы с VK Bridge
- В демо режиме VK Bridge может не работать
- Это нормально, приложение переключится в демо режим 