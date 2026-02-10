#!/bin/bash

# Скрипт для запуска бота на сервере с использованием Docker

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Запуск Football News Bot ===${NC}"

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo -e "${YELLOW}Файл .env не найден. Создаем из примера...${NC}"
    cp .env.example .env
    echo "⚠️  ВАЖНО: Отредактируйте .env файл и добавьте TELEGRAM_BOT_TOKEN"
    echo "Выполните: nano .env"
    exit 1
fi

# Проверка наличия токена
if ! grep -q "TELEGRAM_BOT_TOKEN=." .env; then
    echo "⚠️  ОШИБКА: TELEGRAM_BOT_TOKEN не установлен в .env файле"
    echo "Выполните: nano .env"
    exit 1
fi

# Создаем необходимые директории
mkdir -p data logs

# Останавливаем старый контейнер, если он запущен
echo -e "${YELLOW}Остановка старого контейнера...${NC}"
docker-compose down 2>/dev/null || true

# Собираем и запускаем контейнер
echo -e "${YELLOW}Сборка и запуск контейнера...${NC}"
docker-compose up -d --build

echo -e "${GREEN}=== Бот успешно запущен! ===${NC}"
echo ""
echo "Полезные команды:"
echo "  Просмотр логов:      docker-compose logs -f"
echo "  Остановка бота:      docker-compose down"
echo "  Перезапуск бота:     docker-compose restart"
echo "  Статус контейнера:   docker-compose ps"
