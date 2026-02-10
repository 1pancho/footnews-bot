#!/bin/bash

# Быстрый деплой на VPS через SSH
# Использование: ./deploy/quick_deploy.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Быстрый деплой на VPS ===${NC}"

# Параметры сервера
SERVER_IP="212.113.106.241"
SERVER_USER="root"
SERVER_PATH="/root/football-news-bot"

echo -e "${YELLOW}Копирование файлов на сервер...${NC}"

# Синхронизация файлов
rsync -avz --delete \
    --exclude 'venv/' \
    --exclude '*.pyc' \
    --exclude '__pycache__/' \
    --exclude '.git/' \
    --exclude '*.db' \
    --exclude 'data/' \
    --exclude 'logs/' \
    --exclude '.env' \
    ./ ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/

echo -e "${YELLOW}Перезапуск бота на сервере...${NC}"

# Перезапуск бота
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /root/football-news-bot
docker-compose down
docker-compose up -d --build
echo "Ожидание запуска бота..."
sleep 3
docker-compose ps
echo ""
echo "Последние логи:"
docker-compose logs --tail=30
ENDSSH

echo -e "${GREEN}=== Деплой завершен! ===${NC}"
echo ""
echo "Для просмотра логов: ssh ${SERVER_USER}@${SERVER_IP} 'cd ${SERVER_PATH} && docker-compose logs -f'"
