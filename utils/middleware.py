import time
import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from database.db_manager import db_manager

logger = logging.getLogger(__name__)

class DatabaseMiddleware(BaseMiddleware):
    """Middleware to inject database manager into handlers"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["db"] = db_manager
        return await handler(event, data)

class ThrottlingMiddleware(BaseMiddleware):
    """Middleware to prevent spam and rate limiting"""
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.user_timestamps: Dict[int, float] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id is None:
            return await handler(event, data)
        
        current_time = time.time()
        last_request = self.user_timestamps.get(user_id, 0)
        
        if current_time - last_request < self.rate_limit:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            
            if isinstance(event, Message):
                await event.answer("⚠️ Будь ласка, зачекайте перед наступним повідомленням.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⚠️ Занадто швидкі дії. Зачекайте трохи.", show_alert=True)
            
            return
        
        self.user_timestamps[user_id] = current_time
        return await handler(event, data)

class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging user activities"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()
        
        # Log request
        if isinstance(event, Message):
            logger.info(
                f"Message from user {event.from_user.id} (@{event.from_user.username}): "
                f"{event.text[:100] if event.text else event.content_type}"
            )
        elif isinstance(event, CallbackQuery):
            logger.info(
                f"Callback from user {event.from_user.id} (@{event.from_user.username}): "
                f"{event.data}"
            )
        
        try:
            result = await handler(event, data)
            
            # Log processing time
            processing_time = time.time() - start_time
            if processing_time > 1.0:  # Log slow requests
                logger.warning(f"Slow request processing: {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            
            # Send user-friendly error message
            error_message = "❌ Виникла технічна помилка. Спробуйте пізніше."
            
            try:
                if isinstance(event, Message):
                    await event.answer(error_message)
                elif isinstance(event, CallbackQuery):
                    await event.message.edit_text(error_message)
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
            
            raise

class LanguageMiddleware(BaseMiddleware):
    """Middleware to determine and inject user language"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        # Default language
        language = "uk"
        
        if user_id:
            try:
                # Get user language from database
                user = await db_manager.get_user(user_id)
                if user and user.language:
                    language = user.language
                else:
                    # Try to get from Telegram locale
                    if isinstance(event, Message) and event.from_user.language_code:
                        if event.from_user.language_code.startswith('en'):
                            language = "en"
                    elif isinstance(event, CallbackQuery) and event.from_user.language_code:
                        if event.from_user.language_code.startswith('en'):
                            language = "en"
            except Exception as e:
                logger.error(f"Error getting user language: {e}")
        
        data["language"] = language
        return await handler(event, data)

class SecurityMiddleware(BaseMiddleware):
    """Middleware for security checks and user validation"""
    
    def __init__(self):
        self.blocked_users: set = set()
        self.suspicious_activity: Dict[int, int] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id is None:
            return await handler(event, data)
        
        # Check if user is blocked
        if user_id in self.blocked_users:
            logger.warning(f"Blocked user {user_id} attempted access")
            return
        
        # Check for suspicious activity
        if user_id in self.suspicious_activity:
            self.suspicious_activity[user_id] += 1
            if self.suspicious_activity[user_id] > 10:  # Too many requests
                self.blocked_users.add(user_id)
                logger.warning(f"User {user_id} blocked due to suspicious activity")
                return
        else:
            self.suspicious_activity[user_id] = 1
        
        # Update user activity
        try:
            async with db_manager.pool.acquire() as conn:
                await conn.execute(
                    'UPDATE users SET last_activity = NOW() WHERE user_id = $1',
                    user_id
                )
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
        
        return await handler(event, data)

class AnalyticsMiddleware(BaseMiddleware):
    """Middleware for collecting usage analytics"""
    
    def __init__(self):
        self.daily_stats: Dict[str, int] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Collect analytics data
        today = datetime.now().strftime('%Y-%m-%d')
        
        if isinstance(event, Message):
            self.daily_stats[f"{today}_messages"] = self.daily_stats.get(f"{today}_messages", 0) + 1
            
            # Track command usage
            if event.text and event.text.startswith('/'):
                command = event.text.split()[0]
                self.daily_stats[f"{today}_command_{command}"] = self.daily_stats.get(f"{today}_command_{command}", 0) + 1
                
        elif isinstance(event, CallbackQuery):
            self.daily_stats[f"{today}_callbacks"] = self.daily_stats.get(f"{today}_callbacks", 0) + 1
            
            # Track callback data
            if event.data:
                callback_type = event.data.split('_')[0] if '_' in event.data else event.data
                self.daily_stats[f"{today}_callback_{callback_type}"] = self.daily_stats.get(f"{today}_callback_{callback_type}", 0) + 1
        
        return await handler(event, data)
    
    def get_daily_stats(self, date: str = None) -> Dict[str, int]:
        """Get daily statistics"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        return {k: v for k, v in self.daily_stats.items() if k.startswith(date)}

class MaintenanceMiddleware(BaseMiddleware):
    """Middleware for handling maintenance mode"""
    
    def __init__(self):
        self.maintenance_mode = False
        self.maintenance_message = "🔧 Бот на технічному обслуговуванні. Спробуйте пізніше."
        self.allowed_users = set()  # Admin users who can use bot during maintenance
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not self.maintenance_mode:
            return await handler(event, data)
        
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        # Allow admins during maintenance
        if user_id in self.allowed_users:
            return await handler(event, data)
        
        # Send maintenance message to regular users
        try:
            if isinstance(event, Message):
                await event.answer(self.maintenance_message)
            elif isinstance(event, CallbackQuery):
                await event.answer(self.maintenance_message, show_alert=True)
        except Exception as e:
            logger.error(f"Error sending maintenance message: {e}")
        
        return
    
    def enable_maintenance(self, message: str = None):
        """Enable maintenance mode"""
        self.maintenance_mode = True
        if message:
            self.maintenance_message = message
        logger.info("Maintenance mode enabled")
    
    def disable_maintenance(self):
        """Disable maintenance mode"""
        self.maintenance_mode = False
        logger.info("Maintenance mode disabled")