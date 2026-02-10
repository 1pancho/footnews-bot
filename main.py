"""Main entry point for the news parser bot."""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TELEGRAM_BOT_TOKEN, DATABASE_URL, PARSE_INTERVAL_MINUTES
from database import Database
from bot.handlers import register_handlers
from news_service import NewsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log"),
    ],
)

logger = logging.getLogger(__name__)

# Global variables
db: Database = None
news_service: NewsService = None
scheduler: AsyncIOScheduler = None


async def scheduled_news_update():
    """Scheduled task to update news."""
    logger.info("Running scheduled news update...")
    try:
        new_count = await news_service.update_news()
        logger.info(f"Scheduled update completed. Added {new_count} new articles.")
    except Exception as e:
        logger.error(f"Error in scheduled news update: {e}")


async def on_startup(bot: Bot):
    """Actions on bot startup."""
    global db, news_service, scheduler

    logger.info("Bot starting up...")

    # Initialize database
    db = Database(DATABASE_URL)
    await db.init_db()

    # Initialize news service
    news_service = NewsService(db)

    # Initial news fetch
    logger.info("Performing initial news fetch...")
    await news_service.update_news()

    # Setup scheduler for periodic news updates
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_news_update,
        "interval",
        minutes=PARSE_INTERVAL_MINUTES,
        id="news_update",
    )
    scheduler.start()
    logger.info(
        f"Scheduler started. News will be updated every {PARSE_INTERVAL_MINUTES} minutes."
    )

    logger.info("Bot startup completed!")


async def on_shutdown(bot: Bot):
    """Actions on bot shutdown."""
    global db, scheduler

    logger.info("Bot shutting down...")

    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler stopped")

    if db:
        await db.close()
        logger.info("Database connection closed")

    logger.info("Bot shutdown completed!")


async def main():
    """Main function to run the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Please check your .env file.")
        sys.exit(1)

    # Initialize bot and dispatcher
    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register handlers
    register_handlers(dp)

    # Pass database to handlers
    dp["db"] = db

    # Register startup and shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Start polling
    logger.info("Starting bot polling...")
    try:
        # Update db reference after startup
        await on_startup(bot)
        dp["db"] = db

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await on_shutdown(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
