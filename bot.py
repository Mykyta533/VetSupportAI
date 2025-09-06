import asyncio
import logging
import os
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

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Перевірка обов’язкових змінних середовища
required_env_vars = ['BOT_TOKEN']
for var in required_env_vars:
    if not config.get(var):
        logger.error(f"Відсутня обов’язкова змінна середовища: {var}")
        raise ValueError(f"Змінна середовища {var} не встановлена")

# Логування BOT_TOKEN і порту для дебагу
logger.info(f"Завантажено BOT_TOKEN: {config['BOT_TOKEN'][:10]}...")
port = config.get('PORT', '10000')
logger.info(f"Використовується порт: {port}")

# Ініціалізація бота та диспетчера
try:
    bot = Bot(
        token=config['BOT_TOKEN'],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
except Exception as e:
    logger.error(f"Не вдалося ініціалізувати бота: {e}")
    raise

dp = Dispatcher(storage=MemoryStorage())

async def on_startup(bot: Bot):
    """Ініціалізація бота при старті"""
    try:
        # Ініціалізація бази даних, якщо DATABASE_URL встановлено
        if config.get('DATABASE_URL'):
            try:
                db_manager = DatabaseManager()
                await db_manager.init_database()
                logger.info("База даних успішно ініціалізована")
            except Exception as e:
                logger.error(f"Помилка ініціалізації бази даних: {e}")
                raise
        else:
            logger.warning("DATABASE_URL не встановлено, пропускаємо ініціалізацію бази даних")

        # Закоментований LegalUpdater для уникнення помилки LEGAL_API_URL
        # legal_updater = LegalUpdater()
        # await legal_updater.update_legal_content()
        
        marketing_manager = MarketingManager()
        start_scheduler()

        # Налаштування вебхука або polling
        webhook_base_url = config.get('WEBHOOK_URL')
        if webhook_base_url:
            webhook_url = f"{webhook_base_url}{config['WEBHOOK_PATH']}"
            await bot.set_webhook(
                url=webhook_url,
                secret_token=config['WEBHOOK_SECRET']
            )
            logger.info(f"Вебхук встановлено на {webhook_url}")
        else:
            logger.info("WEBHOOK_URL не встановлено, запускаємо в режимі polling")
            asyncio.create_task(dp.start_polling(bot))

        logger.info("Бот успішно запущено!")
        
    except Exception as e:
        logger.error(f"Помилка під час запуску: {e}")
        raise

async def on_shutdown(bot: Bot):
    """Очищення при завершенні роботи"""
    try:
        if config.get('WEBHOOK_URL'):
            await bot.delete_webhook()
        
        await bot.session.close()
        logger.info("Завершення роботи бота виконано!")
        
    except Exception as e:
        logger.error(f"Помилка під час завершення роботи: {e}")

def setup_handlers():
    """Реєстрація всіх обробників"""
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
    Створює веб-додаток aiohttp та реєструє обробники і middleware.
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
