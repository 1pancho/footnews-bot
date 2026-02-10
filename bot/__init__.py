"""Bot package for Telegram bot."""
from .handlers import register_handlers
from .keyboards import get_main_keyboard, get_clubs_keyboard

__all__ = ["register_handlers", "get_main_keyboard", "get_clubs_keyboard"]
