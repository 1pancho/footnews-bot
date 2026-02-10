#!/bin/bash

# Скрипт для настройки systemd service для автозапуска бота

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Настройка systemd service ===${NC}"

# Получаем текущую директорию
CURRENT_DIR=$(pwd)

# Создаем systemd service файл
SERVICE_FILE="/etc/systemd/system/football-news-bot.service"

echo -e "${YELLOW}Создание service файла: ${SERVICE_FILE}${NC}"

cat > ${SERVICE_FILE} << EOF
[Unit]
Description=Football News Telegram Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${CURRENT_DIR}
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd
echo -e "${YELLOW}Перезагрузка systemd...${NC}"
systemctl daemon-reload

# Включаем автозапуск
echo -e "${YELLOW}Включение автозапуска...${NC}"
systemctl enable football-news-bot.service

# Запускаем сервис
echo -e "${YELLOW}Запуск сервиса...${NC}"
systemctl start football-news-bot.service

# Проверяем статус
echo -e "${GREEN}=== Статус сервиса ===${NC}"
systemctl status football-news-bot.service --no-pager

echo ""
echo -e "${GREEN}=== Настройка завершена! ===${NC}"
echo ""
echo "Полезные команды для управления сервисом:"
echo "  Статус:       systemctl status football-news-bot"
echo "  Запуск:       systemctl start football-news-bot"
echo "  Остановка:    systemctl stop football-news-bot"
echo "  Перезапуск:   systemctl restart football-news-bot"
echo "  Логи:         journalctl -u football-news-bot -f"
echo "  Отключить:    systemctl disable football-news-bot"
