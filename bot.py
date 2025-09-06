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

# Validate BOT_TOKEN before initializing Bot
bot_token = config.get('BOT_TOKEN')
if not bot_token:
    logger.error("BOT_TOKEN is not set in config or environment variables")
    raise ValueError("BOT_TOKEN is not set. Please check environment variables or config.")

logger.info(f"Loaded BOT_TOKEN: {bot_token[:10]}...")  # Log first 10 chars of token for debug

# Initialize bot and dispatcher
try:
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
except Exception as e:
    logger.error(f"Failed to initialize Bot: {e}")
    raise

dp = Dispatcher(storage=MemoryStorage())

async def on_startup(bot: Bot):
    """Initialize bot on startup"""
    try:
        db_manager = DatabaseManager()
        await db_manager.init_database()
        
        # Comment out LegalUpdater to avoid LEGAL_API_URL error
        # legal_updater = LegalUpdater()
        # await legal_updater.update_legal_content()
        
        marketing_manager = MarketingManager()
        
        start_scheduler()
        
        webhook_base_url = config.get('WEBHOOK_URL')
        if webhook_base_url:
            webhook_url = f"{webhook_base_url}{config['WEBHOOK_PATH']}"
            await bot.set_webhook(
                url=webhook_url,
                secret_token=config['WEBHOOK_SECRET']
            )
            logger.info(f"Webhook set to {webhook_url}")
        else:
            logger.warning("WEBHOOK_URL is not set, running in polling mode")
            
        logger.info("Bot started successfully!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

async def on_shutdown(bot: Bot):
    """Cleanup on shutdown"""
    try:
        if config.get('WEBHOOK_URL'):
            await bot.delete_webhook()
        
        await bot.session.close()
        logger.info("Bot shutdown completed!")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

def setup_handlers():
    """Register all handlers"""
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    
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

def create_app() -> web.Application:
    """
    This function creates an aiohttp web application and
    registers handlers and middleware.
    """
    setup_handlers()
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    app = web.Application()
    
    async def health_check(request):
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "VetSupport AI Bot"
        })
    
    app.router.add_get("/health", health_check)
    
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config['WEBHOOK_SECRET']
    )
    
    webhook_requests_handler.register(app, path=config['WEBHOOK_PATH'])
    setup_application(app, dp, bot=bot)
    
    return app

app = create_app()
