import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from database.db_manager import db_manager
from services.legal_updater import LegalUpdater

# Try to import MarketingManager with error handling
try:
    from services.marketing import MarketingManager
    MARKETING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Marketing module not available: {e}")
    MARKETING_AVAILABLE = False
    MarketingManager = None

logger = logging.getLogger(__name__)

class BotScheduler:
    def __init__(self):
        # Initialize MarketingManager with error handling
        self.marketing_manager = None
        if MARKETING_AVAILABLE:
            try:
                self.marketing_manager = MarketingManager()
                logger.info("MarketingManager initialized successfully")
            except Exception as e:
                logger.warning(f"Warning: Marketing disabled: {e}")
                self.marketing_manager = None
        
        # Initialize LegalUpdater with error handling
        self.legal_updater = None
        try:
            self.legal_updater = LegalUpdater()
            logger.info("LegalUpdater initialized successfully")
        except Exception as e:
            logger.warning(f"Warning: Legal updater disabled: {e}")
            self.legal_updater = None
        
        self.running = False
    
    def setup_jobs(self):
        """Setup scheduled jobs"""
        try:
            # Daily tasks
            schedule.every().day.at("09:00").do(self._run_async_job, self.send_daily_tips)
            schedule.every().day.at("20:00").do(self._run_async_job, self.send_mood_reminders)
            schedule.every().day.at("02:00").do(self._run_async_job, self.cleanup_old_data)
            
            # Weekly tasks
            schedule.every().monday.at("10:00").do(self._run_async_job, self.send_weekly_reports)
            schedule.every().sunday.at("18:00").do(self._run_async_job, self.update_legal_content)
            
            # Monthly tasks
            schedule.every().day.at("03:00").do(self._run_async_job, self.monthly_maintenance)
            
            logger.info("Scheduled jobs configured successfully")
        except Exception as e:
            logger.error(f"Error setting up scheduled jobs: {e}")
            raise
    
    def _run_async_job(self, coroutine_func):
        """Helper method to run async functions in scheduled jobs"""
        try:
            # Get current event loop or create new one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, create a task
                    asyncio.create_task(coroutine_func())
                else:
                    # If loop is not running, run until complete
                    loop.run_until_complete(coroutine_func())
            except RuntimeError:
                # No event loop in current thread, create new one
                asyncio.run(coroutine_func())
        except Exception as e:
            logger.error(f"Error running async job {coroutine_func.__name__}: {e}")
    
    async def send_daily_tips(self):
        """Send daily mental health tips to active users"""
        try:
            tips = [
                "🌅 Почніть день з глибокого дихання - це допоможе налаштуватися на позитивний лад.",
                "💪 Навіть 10 хвилин фізичної активності можуть значно покращити ваш настрій.",
                "🧘‍♂️ Спробуйте медитацію усвідомленості - це ефективний спосіб зменшити стрес.",
                "📝 Ведіння щоденника допомагає краще розуміти свої емоції та думки.",
                "🤝 Зв'язок з близькими людьми - важлива частина ментального здоров'я.",
                "🎯 Ставте собі маленькі досяжні цілі - це підвищує самооцінку.",
                "🌿 Проводьте час на природі - це природний антидепресант."
            ]
            
            today_tip = tips[datetime.now().weekday() % len(tips)]
            
            # Check if database connection is available
            if not db_manager or not db_manager.pool:
                logger.error("Database connection not available")
                return
            
            # Get active users
            async with db_manager.pool.acquire() as conn:
                active_users = await conn.fetch('''
                    SELECT user_id FROM users 
                    WHERE last_activity >= NOW() - INTERVAL '7 days'
                    AND subscription_status != 'inactive'
                ''')
            
            # Send tips using marketing manager if available
            if self.marketing_manager:
                try:
                    await self.marketing_manager.send_bulk_message(
                        [user['user_id'] for user in active_users],
                        today_tip
                    )
                    logger.info(f"Daily tip sent to {len(active_users)} users via marketing manager")
                except Exception as e:
                    logger.error(f"Error sending tips via marketing manager: {e}")
            else:
                logger.info(f"Would send daily tip to {len(active_users)} users: {today_tip}")
            
        except Exception as e:
            logger.error(f"Error sending daily tips: {e}")
    
    async def send_mood_reminders(self):
        """Send mood check-in reminders to users who haven't checked in today"""
        try:
            if not db_manager or not db_manager.pool:
                logger.error("Database connection not available")
                return
                
            async with db_manager.pool.acquire() as conn:
                users_without_checkin = await conn.fetch('''
                    SELECT u.user_id, u.first_name, u.language
                    FROM users u
                    LEFT JOIN mood_checkins m ON u.user_id = m.user_id 
                        AND m.timestamp >= CURRENT_DATE
                    WHERE u.last_activity >= NOW() - INTERVAL '3 days'
                    AND m.user_id IS NULL
                    AND u.subscription_status != 'inactive'
                ''')
            
            reminder_text_uk = "🧠 Нагадування: Як ваш настрій сьогодні? Відстежування настрою допомагає краще розуміти себе."
            reminder_text_en = "🧠 Reminder: How is your mood today? Mood tracking helps you understand yourself better."
            
            if self.marketing_manager:
                try:
                    for user in users_without_checkin:
                        text = reminder_text_uk if user['language'] == 'uk' else reminder_text_en
                        await self.marketing_manager.send_message(user['user_id'], text)
                    logger.info(f"Mood reminders sent to {len(users_without_checkin)} users")
                except Exception as e:
                    logger.error(f"Error sending mood reminders via marketing manager: {e}")
            else:
                logger.info(f"Would send mood reminders to {len(users_without_checkin)} users")
            
        except Exception as e:
            logger.error(f"Error sending mood reminders: {e}")
    
    async def send_weekly_reports(self):
        """Send weekly mood reports to users"""
        try:
            if not db_manager or not db_manager.pool:
                logger.error("Database connection not available")
                return
                
            async with db_manager.pool.acquire() as conn:
                users_with_data = await conn.fetch('''
                    SELECT DISTINCT u.user_id, u.first_name, u.language
                    FROM users u
                    JOIN mood_checkins m ON u.user_id = m.user_id
                    WHERE m.timestamp >= NOW() - INTERVAL '7 days'
                    AND u.subscription_status != 'inactive'
                ''')
            
            if self.marketing_manager:
                try:
                    for user in users_with_data:
                        # Generate weekly report for user
                        report = await self._generate_weekly_report(user['user_id'])
                        if report:
                            await self.marketing_manager.send_message(user['user_id'], report)
                    logger.info(f"Weekly reports sent to {len(users_with_data)} users")
                except Exception as e:
                    logger.error(f"Error sending weekly reports via marketing manager: {e}")
            else:
                logger.info(f"Would send weekly reports to {len(users_with_data)} users")
            
        except Exception as e:
            logger.error(f"Error sending weekly reports: {e}")
    
    async def _generate_weekly_report(self, user_id: int) -> Optional[str]:
        """Generate weekly mood report for a user"""
        try:
            if not db_manager or not db_manager.pool:
                return None
                
            async with db_manager.pool.acquire() as conn:
                mood_data = await conn.fetch('''
                    SELECT mood_level, timestamp
                    FROM mood_checkins
                    WHERE user_id = $1 AND timestamp >= NOW() - INTERVAL '7 days'
                    ORDER BY timestamp
                ''', user_id)
            
            if not mood_data:
                return None
            
            avg_mood = sum(record['mood_level'] for record in mood_data) / len(mood_data)
            check_ins = len(mood_data)
            
            report = f"""
📊 Ваш тижневий звіт настрою:
• Середній рівень настрою: {avg_mood:.1f}/5
• Кількість відміток: {check_ins}
• Тенденція: {'📈 Покращується' if mood_data[-1]['mood_level'] > mood_data[0]['mood_level'] else '📉 Знижується' if mood_data[-1]['mood_level'] < mood_data[0]['mood_level'] else '➡️ Стабільно'}

Продовжуйте відстежувати свій настрій для кращого розуміння себе! 💪
            """
            
            return report.strip()
            
        except Exception as e:
            logger.error(f"Error generating weekly report for user {user_id}: {e}")
            return None
    
    async def cleanup_old_data(self):
        """Clean up old data to maintain database performance"""
        try:
            if not db_manager or not db_manager.pool:
                logger.error("Database connection not available")
                return
                
            async with db_manager.pool.acquire() as conn:
                # Clean up old AI chats (keep last 3 months)
                result1 = await conn.execute('''
                    DELETE FROM ai_chats 
                    WHERE timestamp < NOW() - INTERVAL '3 months'
                ''')
                
                # Clean up old mood check-ins (keep last 2 years)
                result2 = await conn.execute('''
                    DELETE FROM mood_checkins 
                    WHERE timestamp < NOW() - INTERVAL '2 years'
                ''')
                
                # Parse result strings to get affected rows count
                deleted_chats = result1.split()[1] if result1.startswith('DELETE') else '0'
                deleted_moods = result2.split()[1] if result2.startswith('DELETE') else '0'
                
                logger.info(f"Cleaned up old data: {deleted_chats} chats, {deleted_moods} mood entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def update_legal_content(self):
        """Update legal content from external sources"""
        try:
            if self.legal_updater:
                await self.legal_updater.update_legal_content()
                logger.info("Legal content updated successfully")
            else:
                logger.warning("Legal updater not available, skipping legal content update")
                
        except Exception as e:
            logger.error(f"Error updating legal content: {e}")
    
    async def monthly_maintenance(self):
        """Perform monthly maintenance tasks"""
        try:
            # Only run on the 1st of each month
            if datetime.now().day != 1:
                return
            
            if not db_manager or not db_manager.pool:
                logger.error("Database connection not available")
                return
            
            async with db_manager.pool.acquire() as conn:
                # Update user statistics
                await conn.execute('''
                    UPDATE user_stats SET
                        total_check_ins = (
                            SELECT COUNT(*) FROM mood_checkins 
                            WHERE user_id = user_stats.user_id
                        ),
                        average_mood = (
                            SELECT AVG(mood_level) FROM mood_checkins 
                            WHERE user_id = user_stats.user_id
                        ),
                        ai_chats_count = (
                            SELECT COUNT(*) FROM ai_chats 
                            WHERE user_id = user_stats.user_id
                        )
                ''')
                
                # Archive old consultations
                await conn.execute('''
                    UPDATE consultations SET status = 'archived'
                    WHERE end_time < NOW() - INTERVAL '6 months'
                    AND status = 'completed'
                ''')
                
                logger.info("Monthly maintenance completed successfully")
                
        except Exception as e:
            logger.error(f"Error in monthly maintenance: {e}")
    
    async def run_scheduler(self):
        """Run the scheduler in background"""
        self.running = True
        logger.info("Scheduler started")
        
        try:
            while self.running:
                schedule.run_pending()
                await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Error in scheduler main loop: {e}")
        finally:
            logger.info("Scheduler loop ended")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Scheduler stopped")

# Global scheduler instance
scheduler = BotScheduler()

def start_scheduler():
    """Start the background scheduler"""
    try:
        scheduler.setup_jobs()
        # Start scheduler in background task
        asyncio.create_task(scheduler.run_scheduler())
        logger.info("Background scheduler started successfully")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise

def stop_scheduler():
    """Stop the background scheduler"""
    try:
        scheduler.stop_scheduler()
        logger.info("Background scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
