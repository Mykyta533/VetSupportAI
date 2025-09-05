import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import List

from database.db_manager import db_manager
from services.marketing import MarketingManager
from services.legal_updater import LegalUpdater

logger = logging.getLogger(__name__)

class BotScheduler:
    def __init__(self):
        self.marketing_manager = MarketingManager()
        self.legal_updater = LegalUpdater()
        self.running = False
    
    def setup_jobs(self):
        """Setup scheduled jobs"""
        # Daily tasks
        schedule.every().day.at("09:00").do(self.send_daily_tips)
        schedule.every().day.at("20:00").do(self.send_mood_reminders)
        schedule.every().day.at("02:00").do(self.cleanup_old_data)
        
        # Weekly tasks
        schedule.every().monday.at("10:00").do(self.send_weekly_reports)
        schedule.every().sunday.at("18:00").do(self.update_legal_content)
        
        # Monthly tasks
        schedule.every().day.at("03:00").do(self.monthly_maintenance)
        
        logger.info("Scheduled jobs configured")
    
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
            
            # Get active users
            async with db_manager.pool.acquire() as conn:
                active_users = await conn.fetch('''
                    SELECT user_id FROM users 
                    WHERE last_activity >= NOW() - INTERVAL '7 days'
                    AND subscription_status != 'inactive'
                ''')
            
            # Send tips (this would integrate with the bot instance)
            logger.info(f"Would send daily tip to {len(active_users)} users: {today_tip}")
            
        except Exception as e:
            logger.error(f"Error sending daily tips: {e}")
    
    async def send_mood_reminders(self):
        """Send mood check-in reminders to users who haven't checked in today"""
        try:
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
            
            logger.info(f"Would send mood reminders to {len(users_without_checkin)} users")
            
        except Exception as e:
            logger.error(f"Error sending mood reminders: {e}")
    
    async def send_weekly_reports(self):
        """Send weekly mood reports to users"""
        try:
            async with db_manager.pool.acquire() as conn:
                users_with_data = await conn.fetch('''
                    SELECT DISTINCT u.user_id, u.first_name, u.language
                    FROM users u
                    JOIN mood_checkins m ON u.user_id = m.user_id
                    WHERE m.timestamp >= NOW() - INTERVAL '7 days'
                    AND u.subscription_status != 'inactive'
                ''')
            
            logger.info(f"Would send weekly reports to {len(users_with_data)} users")
            
        except Exception as e:
            logger.error(f"Error sending weekly reports: {e}")
    
    async def cleanup_old_data(self):
        """Clean up old data to maintain database performance"""
        try:
            async with db_manager.pool.acquire() as conn:
                # Clean up old AI chats (keep last 3 months)
                deleted_chats = await conn.execute('''
                    DELETE FROM ai_chats 
                    WHERE timestamp < NOW() - INTERVAL '3 months'
                ''')
                
                # Clean up old mood check-ins (keep last 2 years)
                deleted_moods = await conn.execute('''
                    DELETE FROM mood_checkins 
                    WHERE timestamp < NOW() - INTERVAL '2 years'
                ''')
                
                logger.info(f"Cleaned up old data: {deleted_chats} chats, {deleted_moods} mood entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def update_legal_content(self):
        """Update legal content from external sources"""
        try:
            await self.legal_updater.update_legal_content()
            logger.info("Legal content updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating legal content: {e}")
    
    async def monthly_maintenance(self):
        """Perform monthly maintenance tasks"""
        try:
            # Only run on the 1st of each month
            if datetime.now().day != 1:
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
                
                logger.info("Monthly maintenance completed")
                
        except Exception as e:
            logger.error(f"Error in monthly maintenance: {e}")
    
    async def run_scheduler(self):
        """Run the scheduler in background"""
        self.running = True
        logger.info("Scheduler started")
        
        while self.running:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Scheduler stopped")

# Global scheduler instance
scheduler = BotScheduler()

def start_scheduler():
    """Start the background scheduler"""
    scheduler.setup_jobs()
    # Start scheduler in background task
    asyncio.create_task(scheduler.run_scheduler())

def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.stop_scheduler()