"""Handlers for the bot."""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import Database
from config import FOOTBALL_CLUBS, MAX_NEWS_PER_REQUEST
from .keyboards import (
    get_main_keyboard,
    get_clubs_keyboard,
    get_clubs_management_keyboard,
    get_confirmation_keyboard,
    get_pagination_keyboard,
)
from .messages import (
    WELCOME_MESSAGE,
    HELP_MESSAGE,
    NO_CLUBS_MESSAGE,
    CLUBS_MANAGEMENT_MESSAGE,
    SELECT_CLUB_MESSAGE,
    YOUR_CLUBS_MESSAGE,
    NO_NEWS_MESSAGE,
    NEWS_HEADER,
    CLUB_ADDED_MESSAGE,
    CLUB_REMOVED_MESSAGE,
    CLUBS_CLEARED_MESSAGE,
    CLUB_ALREADY_ADDED_MESSAGE,
    ERROR_MESSAGE,
)

logger = logging.getLogger(__name__)
router = Router()


def format_news_message(news_item) -> str:
    """Format news item as message."""
    clubs = (
        ", ".join(news_item.clubs_mentioned.split(","))
        if news_item.clubs_mentioned
        else "—"
    )

    message = f"📰 <b>{news_item.title}</b>\n\n"

    if news_item.description:
        message += f"{news_item.description[:200]}...\n\n"

    message += f"⚽️ Клубы: {clubs}\n"
    message += f"📌 Источник: {news_item.source}\n"
    message += f"🔗 <a href='{news_item.url}'>Читать полностью</a>"

    return message


@router.message(Command("start"))
async def cmd_start(message: Message, db: Database):
    """Handle /start command."""
    await db.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    await message.answer(WELCOME_MESSAGE, reply_markup=get_main_keyboard())


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    """Handle /help command."""
    await message.answer(HELP_MESSAGE, reply_markup=get_main_keyboard())


@router.message(Command("clubs"))
@router.message(F.text == "⚽️ Мои клубы")
async def cmd_clubs(message: Message):
    """Handle /clubs command."""
    await message.answer(
        CLUBS_MANAGEMENT_MESSAGE, reply_markup=get_clubs_management_keyboard()
    )


@router.message(F.text == "➕ Добавить клуб")
async def add_club_button(message: Message):
    """Handle add club button."""
    await message.answer(
        SELECT_CLUB_MESSAGE,
        reply_markup=get_clubs_keyboard(FOOTBALL_CLUBS, action="add"),
    )


@router.message(F.text == "❌ Удалить клуб")
async def remove_club_button(message: Message, db: Database):
    """Handle remove club button."""
    user_clubs = await db.get_user_clubs(message.from_user.id)

    if not user_clubs:
        await message.answer(NO_CLUBS_MESSAGE, reply_markup=get_main_keyboard())
        return

    await message.answer(
        "Выберите клуб для удаления:",
        reply_markup=get_clubs_keyboard(user_clubs, action="remove"),
    )


@router.callback_query(F.data == "add_club_menu")
async def callback_add_club_menu(callback: CallbackQuery):
    """Handle add club menu callback."""
    await callback.message.edit_text(
        SELECT_CLUB_MESSAGE,
        reply_markup=get_clubs_keyboard(FOOTBALL_CLUBS, action="add"),
    )
    await callback.answer()


@router.callback_query(F.data == "remove_club_menu")
async def callback_remove_club_menu(callback: CallbackQuery, db: Database):
    """Handle remove club menu callback."""
    user_clubs = await db.get_user_clubs(callback.from_user.id)

    if not user_clubs:
        await callback.message.edit_text(NO_CLUBS_MESSAGE)
        await callback.answer()
        return

    await callback.message.edit_text(
        "Выберите клуб для удаления:",
        reply_markup=get_clubs_keyboard(user_clubs, action="remove"),
    )
    await callback.answer()


@router.callback_query(F.data == "show_my_clubs")
async def callback_show_my_clubs(callback: CallbackQuery, db: Database):
    """Handle show my clubs callback."""
    user_clubs = await db.get_user_clubs(callback.from_user.id)

    if not user_clubs:
        await callback.message.edit_text(NO_CLUBS_MESSAGE)
        await callback.answer()
        return

    clubs_list = "\n".join([f"⚽️ {club}" for club in user_clubs])
    await callback.message.edit_text(
        YOUR_CLUBS_MESSAGE.format(clubs_list),
        reply_markup=get_clubs_management_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("add_club:"))
async def callback_add_club(callback: CallbackQuery, db: Database):
    """Handle add club callback."""
    club_name = callback.data.split(":", 1)[1]

    user_clubs = await db.get_user_clubs(callback.from_user.id)

    if club_name in user_clubs:
        await callback.answer(CLUB_ALREADY_ADDED_MESSAGE.format(club_name), show_alert=True)
        return

    success = await db.add_user_club(callback.from_user.id, club_name)

    if success:
        await callback.answer(CLUB_ADDED_MESSAGE.format(club_name))
    else:
        await callback.answer(ERROR_MESSAGE, show_alert=True)


@router.callback_query(F.data.startswith("remove_club:"))
async def callback_remove_club(callback: CallbackQuery, db: Database):
    """Handle remove club callback."""
    club_name = callback.data.split(":", 1)[1]

    success = await db.remove_user_club(callback.from_user.id, club_name)

    if success:
        await callback.answer(CLUB_REMOVED_MESSAGE.format(club_name))

        # Update keyboard
        user_clubs = await db.get_user_clubs(callback.from_user.id)
        if user_clubs:
            await callback.message.edit_reply_markup(
                reply_markup=get_clubs_keyboard(user_clubs, action="remove")
            )
        else:
            await callback.message.edit_text(NO_CLUBS_MESSAGE)
    else:
        await callback.answer(ERROR_MESSAGE, show_alert=True)


@router.callback_query(F.data == "clear_all_clubs")
async def callback_clear_all_clubs(callback: CallbackQuery):
    """Handle clear all clubs callback."""
    await callback.message.edit_text(
        "Вы уверены, что хотите удалить все клубы?",
        reply_markup=get_confirmation_keyboard("clear_clubs"),
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_clear_clubs")
async def callback_confirm_clear_clubs(callback: CallbackQuery, db: Database):
    """Handle confirm clear clubs callback."""
    success = await db.clear_user_clubs(callback.from_user.id)

    if success:
        await callback.message.edit_text(CLUBS_CLEARED_MESSAGE)
        await callback.answer()
    else:
        await callback.answer(ERROR_MESSAGE, show_alert=True)


@router.message(Command("news"))
@router.message(F.text == "📰 Новости")
async def cmd_news(message: Message, db: Database):
    """Handle /news command."""
    user_clubs = await db.get_user_clubs(message.from_user.id)

    if not user_clubs:
        await message.answer(NO_CLUBS_MESSAGE, reply_markup=get_main_keyboard())
        return

    # Get recent news filtered by user clubs
    news_items = await db.get_recent_news(limit=MAX_NEWS_PER_REQUEST, clubs=user_clubs)

    if not news_items:
        await message.answer(NO_NEWS_MESSAGE, reply_markup=get_main_keyboard())
        return

    # Send news
    await message.answer(NEWS_HEADER)

    for news_item in news_items[:5]:  # Show first 5 news
        try:
            news_text = format_news_message(news_item)
            await message.answer(news_text, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Error sending news: {e}")


@router.callback_query(F.data == "back_to_menu")
async def callback_back_to_menu(callback: CallbackQuery):
    """Handle back to menu callback."""
    await callback.message.edit_text(
        CLUBS_MANAGEMENT_MESSAGE, reply_markup=get_clubs_management_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery):
    """Handle cancel callback."""
    await callback.message.edit_text(
        CLUBS_MANAGEMENT_MESSAGE, reply_markup=get_clubs_management_keyboard()
    )
    await callback.answer()


def register_handlers(router_to_include: Router):
    """Register all handlers."""
    router_to_include.include_router(router)
