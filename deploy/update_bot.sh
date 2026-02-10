#!/bin/bash

# Скрипт для обновления бота на сервере

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Обновление Football News Bot ===${NC}"

# Останавливаем бота
echo -e "${YELLOW}Остановка бота...${NC}"
docker-compose down

# Обновляем код из git (если используется)
if [ -d .git ]; then
    echo -e "${YELLOW}Обновление кода из git...${NC}"
    git pull
fi

# Пересобираем и запускаем контейнер
echo -e "${YELLOW}Пересборка и запуск контейнера...${NC}"
docker-compose up -d --build

echo -e "${GREEN}=== Обновление завершено! ===${NC}"

# Показываем логи
echo -e "${YELLOW}Логи бота:${NC}"
docker-compose logs --tail=50
