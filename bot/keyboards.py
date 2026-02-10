"""Keyboards for the bot."""
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import List


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📰 Новости"),
        KeyboardButton(text="⚽️ Мои клубы"),
    )
    builder.row(
        KeyboardButton(text="➕ Добавить клуб"),
        KeyboardButton(text="❌ Удалить клуб"),
    )
    builder.row(KeyboardButton(text="ℹ️ Помощь"))

    return builder.as_markup(resize_keyboard=True)


def get_clubs_keyboard(clubs: List[str], action: str = "add") -> InlineKeyboardMarkup:
    """Get inline keyboard with clubs."""
    builder = InlineKeyboardBuilder()

    for club in clubs:
        callback_data = f"{action}_club:{club}"
        builder.row(InlineKeyboardButton(text=club, callback_data=callback_data))

    # Add back button
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu"))

    return builder.as_markup()


def get_clubs_management_keyboard() -> InlineKeyboardMarkup:
    """Get clubs management keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="➕ Добавить клуб", callback_data="add_club_menu")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Мои клубы", callback_data="show_my_clubs")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Удалить клуб", callback_data="remove_club_menu")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Очистить все", callback_data="clear_all_clubs")
    )
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu"))

    return builder.as_markup()


def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """Get confirmation keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}"),
        InlineKeyboardButton(text="❌ Нет", callback_data="cancel"),
    )

    return builder.as_markup()


def get_pagination_keyboard(
    current_page: int, total_pages: int, prefix: str = "news"
) -> InlineKeyboardMarkup:
    """Get pagination keyboard."""
    builder = InlineKeyboardBuilder()

    buttons = []

    if current_page > 0:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"{prefix}_page:{current_page - 1}"
            )
        )

    buttons.append(
        InlineKeyboardButton(
            text=f"{current_page + 1}/{total_pages}", callback_data="current_page"
        )
    )

    if current_page < total_pages - 1:
        buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️", callback_data=f"{prefix}_page:{current_page + 1}"
            )
        )

    builder.row(*buttons)
    builder.row(InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_menu"))

    return builder.as_markup()
