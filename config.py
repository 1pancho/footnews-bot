"""Configuration settings for the news parser bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./news_bot.db")

# Parser settings
PARSE_INTERVAL_MINUTES = int(os.getenv("PARSE_INTERVAL_MINUTES", "30"))
MAX_NEWS_PER_REQUEST = int(os.getenv("MAX_NEWS_PER_REQUEST", "10"))

# Popular football clubs (can be extended)
FOOTBALL_CLUBS = [
    # Российские клубы
    "Спартак", "ЦСКА", "Зенит", "Динамо", "Локомотив", "Краснодар",
    "Ростов", "Рубин", "Сочи", "Урал", "Крылья Советов",
    # Европейские клубы
    "Реал Мадрид", "Барселона", "Бавария", "Манчестер Юнайтед",
    "Манчестер Сити", "Ливерпуль", "Челси", "Арсенал", "ПСЖ",
    "Ювентус", "Интер", "Милан", "Атлетико", "Боруссия",
    "Аякс", "Бенфика", "Порту"
]

# News sources
NEWS_SOURCES = {
    "sports_ru": {
        "name": "Sports.ru",
        "url": "https://www.sports.ru/football/",
        "enabled": True
    },
    "championat": {
        "name": "Championat.com",
        "url": "https://www.championat.com/football/",
        "enabled": True
    },
    "soccer_ru": {
        "name": "Soccer.ru",
        "url": "https://soccer.ru/",
        "enabled": True
    }
}
