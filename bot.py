import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import config
from database.db_manager import DatabaseManager
from handlers import (
    start_handler,
    mood_handler,
    recommendations_handler,
    ai_chat_handler,
    voice_handler,
    stats_handler,
    psychologist_handler,
    legal_handler,
    telemedicine_handler,
    premium_handler,
    hotlines_handler,
    admin_handler
)
from services.scheduler import start_scheduler
from services.legal_updater import LegalUpdater
from services.marketing import MarketingManager
from utils.middleware import (
    DatabaseMiddleware,
    ThrottlingMiddleware,
    LoggingMiddleware,
    LanguageMiddleware
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

async def on_startup():
    """Initialize bot on startup"""
    try:
        # Initialize database
        db_manager = DatabaseManager()
        await db_manager.init_database()
        
        # Initialize legal updater
        legal_updater = LegalUpdater()
        await legal_updater.update_legal_content()
        
        # Initialize marketing manager
        marketing_manager = MarketingManager()
        
        # Start scheduler for automated tasks
        start_scheduler()
        
        # Set webhook if URL is provided
        if config.WEBHOOK_URL:
            webhook_url = f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}"
            await bot.set_webhook(
                url=webhook_url,
                secret_token=config.WEBHOOK_SECRET
            )
            logger.info(f"Webhook set to {webhook_url}")
        
        logger.info("Bot started successfully!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

async def on_shutdown():
    """Cleanup on shutdown"""
    try:
        if config.WEBHOOK_URL:
            await bot.delete_webhook()
        
        await bot.session.close()
        logger.info("Bot shutdown completed!")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

def setup_handlers():
    """Register all handlers"""
    # Register middlewares
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    
    # Register handlers
    dp.include_router(start_handler.router)
    dp.include_router(mood_handler.router)
    dp.include_router(recommendations_handler.router)
    dp.include_router(ai_chat_handler.router)
    dp.include_router(voice_handler.router)
    dp.include_router(stats_handler.router)
    dp.include_router(psychologist_handler.router)
    dp.include_router(legal_handler.router)
    dp.include_router(telemedicine_handler.router)
    dp.include_router(premium_handler.router)
    dp.include_router(hotlines_handler.router)
    dp.include_router(admin_handler.router)

async def main():
    """Main application entry point"""
    setup_handlers()
    
    if config.WEBHOOK_URL:
        # Webhook mode
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=config.WEBHOOK_SECRET
        )
        webhook_requests_handler.register(app, path=config.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        web.run_app(app, host=config.HOST, port=config.PORT)
    else:
        # Polling mode
        await on_startup()
        try:
            await dp.start_polling(bot)
        finally:
            await on_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")