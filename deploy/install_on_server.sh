#!/bin/bash

# Скрипт для установки бота на VPS сервер
# Запускать локально: ./deploy/install_on_server.sh

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Установка Football News Bot на VPS ===${NC}"

# Параметры сервера
SERVER_IP="212.113.106.241"
SERVER_USER="root"
SERVER_PATH="/root/football-news-bot"

# Проверка наличия ssh
if ! command -v ssh &> /dev/null; then
    echo -e "${RED}Ошибка: ssh не установлен${NC}"
    exit 1
fi

echo -e "${YELLOW}Подключение к серверу ${SERVER_IP}...${NC}"

# Создаем временный скрипт для выполнения на сервере
cat > /tmp/server_install.sh << 'EOF'
#!/bin/bash
set -e

echo "=== Обновление системы ==="
apt-get update
apt-get upgrade -y

echo "=== Установка необходимых пакетов ==="
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    docker.io \
    docker-compose \
    nano

# Запуск Docker
systemctl start docker
systemctl enable docker

echo "=== Установка завершена ==="
EOF

# Копируем и выполняем скрипт на сервере
echo -e "${YELLOW}Копирование скрипта на сервер...${NC}"
scp /tmp/server_install.sh ${SERVER_USER}@${SERVER_IP}:/tmp/

echo -e "${YELLOW}Выполнение установки на сервере...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "bash /tmp/server_install.sh"

# Создаем директорию для проекта
echo -e "${YELLOW}Создание директории проекта...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${SERVER_PATH}"

# Копируем файлы проекта
echo -e "${YELLOW}Копирование файлов проекта...${NC}"
rsync -avz --exclude 'venv' --exclude '*.pyc' --exclude '__pycache__' \
    --exclude '.git' --exclude '*.db' --exclude 'data' --exclude 'logs' \
    ./ ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/

echo -e "${GREEN}=== Установка завершена! ===${NC}"
echo -e "${YELLOW}Следующие шаги:${NC}"
echo "1. Подключитесь к серверу: ssh ${SERVER_USER}@${SERVER_IP}"
echo "2. Перейдите в директорию: cd ${SERVER_PATH}"
echo "3. Настройте .env файл: nano .env"
echo "4. Запустите бота: ./deploy/start_bot.sh"

# Очистка
rm /tmp/server_install.sh
