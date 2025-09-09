import asyncio
import os
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

config = {
    "BOT_TOKEN": os.getenv("BOT_TOKEN"),
    "WEBHOOK_URL": "https://vetsupportai-1.onrender.com",
    "WEBHOOK_PATH": os.getenv("WEBHOOK_PATH", "/webhook"),
    "WEBHOOK_SECRET": os.getenv("WEBHOOK_SECRET", "vetsupport_webhook_secret"),
    "DATABASE_URL": os.getenv("DATABASE_URL", ""),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "GROK_API_KEY": os.getenv("GROK_API_KEY", ""),
    "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY", ""),
    "GOOGLE_TTS_KEY": os.getenv("GOOGLE_TTS_KEY", ""),
    "WHISPER_API_KEY": os.getenv("WHISPER_API_KEY", ""),
    "HELSI_API_KEY": os.getenv("HELSI_API_KEY", ""),
    "DOCTOR_ONLINE_API_KEY": os.getenv("DOCTOR_ONLINE_API_KEY", ""),
    "FACEBOOK_TOKEN": os.getenv("FACEBOOK_TOKEN", ""),
    "INSTAGRAM_TOKEN": os.getenv("INSTAGRAM_TOKEN", ""),
    "LINKEDIN_TOKEN": os.getenv("LINKEDIN_TOKEN", ""),
    "ADMIN_CHAT_ID": os.getenv("ADMIN_CHAT_ID", ""),
    "SUPPORT_CHAT_ID": os.getenv("SUPPORT_CHAT_ID", ""),
    "SECRET_KEY": os.getenv("SECRET_KEY", ""),
    "HOST": "0.0.0.0",
    "PORT": "10000"
}

# Логування значень змінних для дебагу
for key, value in config.items():
    if value and isinstance(value, str):  # Перевіряємо, що значення є рядком і не порожнє
        if key == "BOT_TOKEN":
            logger.info(f"{key}: {value[:10]}...")  # Логуємо перші 10 символів для безпеки
        else:
            logger.info(f"{key}: {value}")
    else:
        logger.info(f"{key}: {value}")

# Перевірка тільки BOT_TOKEN як обов’язкової змінної
if not config["BOT_TOKEN"]:
    logger.error("Критична змінна середовища BOT_TOKEN не встановлена")
    raise ValueError("Критична змінна середовища BOT_TOKEN не встановлена")

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

# Validate required environment variables
required_env_vars = ['BOT_TOKEN']
for var in required_env_vars:
    if not config.get(var):
        logger.error(f"Missing required environment variable: {var}")
        raise ValueError(f"Environment variable {var} is not set")

# Optional environment variables with defaults
config.setdefault('WEBHOOK_URL', '')
config.setdefault('WEBHOOK_PATH', '/webhook')
config.setdefault('WEBHOOK_SECRET', '')
config.setdefault('DATABASE_URL', '')
config.setdefault('GEMINI_API_KEY', '')
config.setdefault('OPENAI_API_KEY', '')
config.setdefault('ADMIN_CHAT_ID', '')

# Log BOT_TOKEN for debugging (first 10 chars only for security)
logger.info(f"Loaded BOT_TOKEN: {config['BOT_TOKEN'][:10]}...")

# Initialize bot and dispatcher
try:
    bot = Bot(
        token=config['BOT_TOKEN'],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
except Exception as e:
    logger.error(f"Failed to initialize Bot: {e}")
    raise

dp = Dispatcher(storage=MemoryStorage())

async def on_startup(bot: Bot):
    """Initialize bot on startup"""
    try:
        # Initialize database
        if config['DATABASE_URL']:
            db_manager = DatabaseManager()
            await db_manager.init_database()
            logger.info("Database initialized successfully")
        else:
            logger.warning("DATABASE_URL not set, skipping database initialization")

        # Comment out LegalUpdater to avoid LEGAL_API_URL error
        # legal_updater = LegalUpdater()
        # await legal_updater.update_legal_content()
        
        marketing_manager = MarketingManager()
        start_scheduler()

        # Set webhook if WEBHOOK_URL is provided, otherwise use polling
        webhook_base_url = config.get('WEBHOOK_URL')
        if webhook_base_url:
            webhook_url = f"{webhook_base_url}{config['WEBHOOK_PATH']}"
            await bot.set_webhook(
                url=webhook_url,
                secret_token=config['WEBHOOK_SECRET']
            )
            logger.info(f"Webhook set to {webhook_url}")
        else:
            logger.info("WEBHOOK_URL not set, running in polling mode")
            asyncio.create_task(dp.start_polling(bot))

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
    
    async def status(request):
        return web.json_response({
            "status": "running",
            "webhook": bool(config.get('WEBHOOK_URL')),
            "timestamp": datetime.now().isoformat()
        })
    
    async def db_status(request):
        status = "not_configured"
        if config.get('DATABASE_URL'):
            try:
                db_manager = DatabaseManager()
                await db_manager.init_database()
                status = "connected"
            except Exception as e:
                status = f"error: {str(e)}"
        return web.json_response({
            "database_status": status,
            "timestamp": datetime.now().isoformat()
        })
    
    app.router.add_get("/health", health_check)
    app.router.add_get("/status", status)
    app.router.add_get("/db-status", db_status)
    
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config['WEBHOOK_SECRET']
    )
    
    webhook_requests_handler.register(app, path=config['WEBHOOK_PATH'])
    setup_application(app, dp, bot=bot)
    
    return app

if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host=config.get('HOST', '0.0.0.0'), port=int(config.get('PORT', 10000)))
