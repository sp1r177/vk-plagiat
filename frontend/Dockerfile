FROM node:16-alpine

WORKDIR /app

# Копирование файлов зависимостей
COPY package*.json ./

# Установка зависимостей
RUN npm ci --only=production

# Копирование кода приложения
COPY . .

# Создание пользователя для безопасности
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Изменение владельца файлов
RUN chown -R nextjs:nodejs /app
USER nextjs

# Открытие порта
EXPOSE 3000

# Команда запуска
CMD ["npm", "start"] 