#!/bin/bash

# Автоматический деплой на VPS
# Запустите: ./deploy_to_server.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVER_IP="212.113.106.241"
SERVER_USER="root"
SERVER_PATH="/root/football-news-bot"

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🚀 Football News Bot - Auto Deploy          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}📋 Параметры деплоя:${NC}"
echo -e "   Сервер: ${GREEN}${SERVER_IP}${NC}"
echo -e "   Пользователь: ${GREEN}${SERVER_USER}${NC}"
echo -e "   Путь: ${GREEN}${SERVER_PATH}${NC}"
echo ""

# Проверка соединения
echo -e "${YELLOW}🔍 Проверка доступности сервера...${NC}"
if ! ping -c 1 ${SERVER_IP} &> /dev/null; then
    echo -e "${RED}❌ Сервер недоступен!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Сервер доступен${NC}"
echo ""

# Шаг 1: Установка необходимых пакетов на сервере
echo -e "${YELLOW}📦 Шаг 1/5: Установка пакетов на сервере...${NC}"
cat > /tmp/server_install.sh << 'SERVERSCRIPT'
#!/bin/bash
set -e

echo "Обновление системы..."
apt-get update -y
apt-get upgrade -y

echo "Установка необходимых пакетов..."
apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    nano

echo "Установка Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

echo "Установка Docker Compose..."
if ! docker compose version &> /dev/null; then
    apt-get install -y docker-compose-plugin
fi

echo "Запуск Docker..."
systemctl start docker
systemctl enable docker

echo "✅ Установка завершена!"
SERVERSCRIPT

echo -e "${BLUE}Копирование скрипта установки на сервер...${NC}"
scp /tmp/server_install.sh ${SERVER_USER}@${SERVER_IP}:/tmp/

echo -e "${BLUE}Выполнение установки на сервере...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "bash /tmp/server_install.sh"

echo -e "${GREEN}✅ Пакеты установлены${NC}"
echo ""

# Шаг 2: Создание директории
echo -e "${YELLOW}📁 Шаг 2/5: Создание директории проекта...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${SERVER_PATH}"
echo -e "${GREEN}✅ Директория создана${NC}"
echo ""

# Шаг 3: Копирование файлов
echo -e "${YELLOW}📤 Шаг 3/5: Копирование файлов проекта...${NC}"
rsync -avz --progress \
    --exclude 'venv/' \
    --exclude '*.pyc' \
    --exclude '__pycache__/' \
    --exclude '.git/' \
    --exclude '*.db' \
    --exclude 'data/' \
    --exclude 'logs/' \
    --exclude '.env' \
    ./ ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/

echo -e "${GREEN}✅ Файлы скопированы${NC}"
echo ""

# Шаг 4: Настройка .env
echo -e "${YELLOW}⚙️  Шаг 4/5: Настройка конфигурации...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /root/football-news-bot

# Создание .env файла
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Файл .env создан из примера"
fi

# Создание директорий
mkdir -p data logs

echo "✅ Конфигурация готова"
ENDSSH

echo -e "${GREEN}✅ Конфигурация настроена${NC}"
echo ""

# Шаг 5: Запуск бота
echo -e "${YELLOW}🚀 Шаг 5/5: Запуск бота...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /root/football-news-bot

# Проверка токена
if ! grep -q "TELEGRAM_BOT_TOKEN=." .env; then
    echo ""
    echo "⚠️  ВНИМАНИЕ: Токен бота не установлен!"
    echo ""
    echo "Для запуска бота нужно:"
    echo "1. Получить токен у @BotFather в Telegram"
    echo "2. Выполнить на сервере:"
    echo "   nano /root/football-news-bot/.env"
    echo "3. Добавить: TELEGRAM_BOT_TOKEN=ваш_токен"
    echo "4. Запустить: cd /root/football-news-bot && docker compose up -d"
    echo ""
    exit 0
fi

# Остановка старого контейнера
docker compose down 2>/dev/null || true

# Запуск нового контейнера
docker compose up -d --build

echo "Ожидание запуска..."
sleep 5

# Проверка статуса
docker compose ps

echo ""
echo "Последние логи:"
docker compose logs --tail=30

ENDSSH

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ✅ Деплой завершен!                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}📝 Следующие шаги:${NC}"
echo ""
echo -e "1. ${GREEN}Создайте бота в Telegram:${NC}"
echo -e "   • Откройте @BotFather"
echo -e "   • Отправьте /newbot"
echo -e "   • Скопируйте токен"
echo ""
echo -e "2. ${GREEN}Добавьте токен на сервере:${NC}"
echo -e "   ${BLUE}ssh ${SERVER_USER}@${SERVER_IP}${NC}"
echo -e "   ${BLUE}nano ${SERVER_PATH}/.env${NC}"
echo -e "   Добавьте: TELEGRAM_BOT_TOKEN=ваш_токен"
echo ""
echo -e "3. ${GREEN}Запустите бота:${NC}"
echo -e "   ${BLUE}cd ${SERVER_PATH}${NC}"
echo -e "   ${BLUE}docker compose up -d${NC}"
echo ""
echo -e "4. ${GREEN}Проверьте логи:${NC}"
echo -e "   ${BLUE}docker compose logs -f${NC}"
echo ""
echo -e "${YELLOW}🔗 Полезные команды:${NC}"
echo -e "   Подключение к серверу:  ${BLUE}ssh ${SERVER_USER}@${SERVER_IP}${NC}"
echo -e "   Просмотр логов:         ${BLUE}docker compose logs -f${NC}"
echo -e "   Перезапуск:             ${BLUE}docker compose restart${NC}"
echo -e "   Остановка:              ${BLUE}docker compose down${NC}"
echo ""
echo -e "${GREEN}🎉 GitHub:${NC} https://github.com/1pancho/footnews-bot"
echo ""
