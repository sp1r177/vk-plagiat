#!/bin/bash

echo "🚀 Запуск демо версии Плагиат-Детектор"

# Проверяем наличие Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен. Установите Node.js 18+ и попробуйте снова."
    exit 1
fi

# Проверяем версию Node.js
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Требуется Node.js версии 18 или выше. Текущая версия: $(node -v)"
    exit 1
fi

echo "✅ Node.js версия: $(node -v)"

# Переходим в папку frontend
cd frontend

# Проверяем наличие node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Устанавливаем зависимости..."
    npm install
fi

echo "🎯 Запускаем приложение..."
echo "📍 Приложение будет доступно по адресу: http://localhost:3000"
echo "🔧 Демо режим: приложение работает без backend с тестовыми данными"
echo ""
echo "Для остановки нажмите Ctrl+C"

# Запускаем приложение
npm start 