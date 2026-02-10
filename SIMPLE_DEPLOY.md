# 🚀 Простая инструкция по деплою (3 шага)

Ваш токен бота: `8338541340:AAFAU8borNmPTOZc8J2UEYiNSn1q29gXcQo`
Пароль сервера: `8ce6TqVhw52C`

---

## Шаг 1: Скопируйте эти команды и выполните по очереди

### 1.1. Подключитесь к серверу:

```bash
ssh root@212.113.106.241
```
**Введите пароль:** `8ce6TqVhw52C`

### 1.2. На сервере выполните установку:

```bash
# Обновление системы
apt-get update -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Установка Docker Compose
apt-get install -y docker-compose-plugin git

# Запуск Docker
systemctl start docker
systemctl enable docker

# Проверка
docker --version
docker compose version
```

### 1.3. Клонируйте проект с GitHub:

```bash
cd /root
git clone https://github.com/1pancho/footnews-bot.git football-news-bot
cd football-news-bot
```

---

## Шаг 2: Создайте .env файл с токеном

```bash
cat > .env << 'EOF'
# Telegram Bot Token
TELEGRAM_BOT_TOKEN=8338541340:AAFAU8borNmPTOZc8J2UEYiNSn1q29gXcQo

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/news_bot.db

# Parser settings
PARSE_INTERVAL_MINUTES=30
MAX_NEWS_PER_REQUEST=10
EOF
```

---

## Шаг 3: Запустите бота

```bash
# Создайте необходимые директории
mkdir -p data logs

# Запустите бота
docker compose up -d --build

# Проверьте статус
docker compose ps

# Посмотрите логи
docker compose logs --tail=50 -f
```

**Для выхода из просмотра логов нажмите:** `Ctrl+C`

---

## ✅ Готово!

Теперь откройте Telegram и отправьте вашему боту `/start`

---

## 🔧 Полезные команды (на сервере)

```bash
# Просмотр логов
docker compose logs -f

# Перезапуск бота
docker compose restart

# Остановка бота
docker compose down

# Запуск бота
docker compose up -d

# Проверка статуса
docker compose ps

# Обновление бота (после изменений в коде)
git pull
docker compose up -d --build
```

---

## 📊 Проверка работы

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте `/start`
4. Бот должен ответить приветствием!

---

## 🎯 Быстрая команда (ВСЁ В ОДНОМ)

Если хотите выполнить всё одной командой, скопируйте это:

```bash
ssh root@212.113.106.241 << 'ALLEOF'
# Установка
apt-get update -y
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && rm get-docker.sh
apt-get install -y docker-compose-plugin git
systemctl start docker && systemctl enable docker

# Клонирование проекта
cd /root
git clone https://github.com/1pancho/footnews-bot.git football-news-bot || (cd football-news-bot && git pull)
cd football-news-bot

# Создание .env
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=8338541340:AAFAU8borNmPTOZc8J2UEYiNSn1q29gXcQo
DATABASE_URL=sqlite+aiosqlite:///./data/news_bot.db
PARSE_INTERVAL_MINUTES=30
MAX_NEWS_PER_REQUEST=10
EOF

# Запуск
mkdir -p data logs
docker compose down 2>/dev/null || true
docker compose up -d --build

echo ""
echo "═════════════════════════════════════"
echo "  ✅ БОТ ЗАПУЩЕН!"
echo "═════════════════════════════════════"
echo ""

docker compose ps
echo ""
docker compose logs --tail=30

ALLEOF
```

**Введите пароль:** `8ce6TqVhw52C`

---

## ❓ Если что-то не работает

### Бот не отвечает:
```bash
ssh root@212.113.106.241
cd /root/football-news-bot
docker compose logs
```

### Переустановка:
```bash
ssh root@212.113.106.241
cd /root/football-news-bot
docker compose down
docker compose up -d --build
```

---

**Готово! Теперь ваш бот работает 24/7 на сервере!** 🎉
