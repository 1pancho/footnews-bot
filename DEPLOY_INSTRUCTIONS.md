# 🚀 Инструкция по деплою на VPS

## ⚠️ ВАЖНО ПО БЕЗОПАСНОСТИ

**НИКОГДА** не храните чувствительную информацию в коде или документации:
- Пароли от сервера
- Токены ботов
- API ключи
- Приватные ключи

---

## Шаг 1: Подключитесь к серверу

```bash
ssh root@YOUR_SERVER_IP
```

Введите ваш пароль при запросе.

---

## Шаг 2: Установите Docker

```bash
# Обновление системы
apt-get update -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Установка Docker Compose и git
apt-get install -y docker-compose-plugin git

# Запуск Docker
systemctl start docker
systemctl enable docker

# Проверка установки
docker --version
docker compose version
```

---

## Шаг 3: Клонируйте проект

```bash
cd /root
git clone https://github.com/1pancho/footnews-bot.git football-news-bot
cd football-news-bot
```

---

## Шаг 4: Создайте .env файл

```bash
nano .env
```

Добавьте следующее содержимое (замените значения на свои):

```env
# Telegram Bot Token (получите у @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/news_bot.db

# Parser settings
PARSE_INTERVAL_MINUTES=30
MAX_NEWS_PER_REQUEST=10
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## Шаг 5: Запустите бота

```bash
# Создайте директории
mkdir -p data logs

# Запустите бота
docker compose up -d --build

# Проверьте статус
docker compose ps

# Просмотрите логи
docker compose logs --tail=50 -f
```

**Для выхода из просмотра логов:** `Ctrl+C`

---

## ✅ Проверка работы

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте `/start`
4. Бот должен ответить!

---

## 🔧 Управление ботом

### Просмотр логов
```bash
cd /root/football-news-bot
docker compose logs -f
```

### Перезапуск
```bash
docker compose restart
```

### Остановка
```bash
docker compose down
```

### Обновление кода
```bash
git pull
docker compose up -d --build
```

### Статус
```bash
docker compose ps
```

---

## 🛡️ Рекомендации по безопасности

### 1. Используйте SSH-ключи вместо паролей

```bash
# На вашем компьютере
ssh-keygen -t ed25519

# Копируйте ключ на сервер
ssh-copy-id root@YOUR_SERVER_IP
```

### 2. Отключите вход по паролю

После настройки SSH-ключей:

```bash
# На сервере
nano /etc/ssh/sshd_config

# Измените:
PasswordAuthentication no

# Перезапустите SSH
systemctl restart sshd
```

### 3. Настройте firewall

```bash
# Разрешить только SSH
ufw allow 22/tcp
ufw enable
```

### 4. Регулярно обновляйте систему

```bash
apt-get update && apt-get upgrade -y
```

---

## 🔄 Автозапуск при перезагрузке

```bash
cd /root/football-news-bot
sudo ./deploy/setup_systemd.sh
```

---

## 📱 Получение токена бота

1. Откройте Telegram
2. Найдите [@BotFather](https://t.me/BotFather)
3. Отправьте `/newbot`
4. Следуйте инструкциям
5. Скопируйте токен

---

## 🆘 Решение проблем

### Бот не запускается

```bash
# Проверьте логи
docker compose logs

# Проверьте .env файл
cat .env

# Пересоберите контейнер
docker compose down
docker compose up -d --build
```

### Ошибки Docker

```bash
# Проверьте статус Docker
systemctl status docker

# Перезапустите Docker
systemctl restart docker
```

### Нет места на диске

```bash
# Очистка Docker
docker system prune -a

# Проверка места
df -h
```

---

## 📚 Дополнительная документация

- [README.md](README.md) - Основная документация
- [DEPLOY.md](DEPLOY.md) - Подробный гайд по деплою
- [GitHub репозиторий](https://github.com/1pancho/footnews-bot)

---

**Готово! Ваш бот работает!** 🎉
