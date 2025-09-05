import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from database.db_manager import db_manager
from config import config

logger = logging.getLogger(__name__)

class MarketingManager:
    def __init__(self):
        self.facebook_token = config.FACEBOOK_TOKEN
        self.instagram_token = config.INSTAGRAM_TOKEN
        self.linkedin_token = config.LINKEDIN_TOKEN
        self.auto_post_channels = config.AUTO_POST_CHANNELS
        
    async def create_daily_content(self):
        """Create and schedule daily content"""
        try:
            # Mental health tips
            tips = await self.get_daily_tips()
            
            # Success stories (anonymized)
            stories = await self.get_success_stories()
            
            # Educational content
            educational = await self.get_educational_content()
            
            # Schedule posts
            await self.schedule_social_media_posts(tips + stories + educational)
            
        except Exception as e:
            logger.error(f"Error creating daily content: {e}")
    
    async def get_daily_tips(self) -> List[Dict[str, Any]]:
        """Generate daily mental health tips"""
        tips = [
            {
                "type": "tip",
                "content_uk": "🌅 Ранкова рутина допомагає структурувати день та покращити настрій. Почніть з простих дій: прокинутися в один час, випити склянку води, зробити кілька глибоких вдихів.",
                "content_en": "🌅 Morning routine helps structure your day and improve mood. Start with simple actions: wake up at the same time, drink a glass of water, take a few deep breaths.",
                "hashtags": ["#МентальнеЗдоровя", "#ВетераниУкраїни", "#ПсихологічнаПідтримка", "#MentalHealth", "#UkrainianVeterans"],
                "image_url": "https://images.pexels.com/photos/1051838/pexels-photo-1051838.jpeg"
            },
            {
                "type": "tip",
                "content_uk": "💪 Фізична активність - природний антидепресант. Навіть 15 хвилин ходьби можуть значно покращити ваш настрій та зменшити стрес.",
                "content_en": "💪 Physical activity is a natural antidepressant. Even 15 minutes of walking can significantly improve your mood and reduce stress.",
                "hashtags": ["#ФізичнаАктивність", "#ЗдоровийСпосібЖиття", "#ВетераниУкраїни", "#PhysicalActivity", "#HealthyLifestyle"],
                "image_url": "https://images.pexels.com/photos/416978/pexels-photo-416978.jpeg"
            },
            {
                "type": "tip",
                "content_uk": "🧘‍♂️ Медитація усвідомленості допомагає зосередитися на теперішньому моменті та зменшити тривожність. Почніть з 5 хвилин на день.",
                "content_en": "🧘‍♂️ Mindfulness meditation helps focus on the present moment and reduce anxiety. Start with 5 minutes a day.",
                "hashtags": ["#Медитація", "#Усвідомленість", "#ПсихологічнеЗдоровя", "#Meditation", "#Mindfulness"],
                "image_url": "https://images.pexels.com/photos/3822622/pexels-photo-3822622.jpeg"
            }
        ]
        
        return tips
    
    async def get_success_stories(self) -> List[Dict[str, Any]]:
        """Get anonymized success stories"""
        try:
            # Get aggregated statistics for success stories
            async with db_manager.pool.acquire() as conn:
                stats = await conn.fetchrow('''
                    SELECT 
                        COUNT(*) as total_users,
                        COUNT(*) FILTER (WHERE subscription_status = 'premium') as premium_users,
                        AVG(average_mood) as avg_mood,
                        COUNT(*) FILTER (WHERE streak_days >= 7) as consistent_users
                    FROM user_stats us
                    JOIN users u ON us.user_id = u.user_id
                    WHERE u.last_activity >= NOW() - INTERVAL '30 days'
                ''')
            
            if stats:
                stories = [
                    {
                        "type": "success",
                        "content_uk": f"📈 Наші користувачі показують чудові результати! Середній рівень настрою покращився до {stats['avg_mood']:.1f}/10. {stats['consistent_users']} людей ведуть щоденник настрою більше тижня поспіль!",
                        "content_en": f"📈 Our users show great results! Average mood level improved to {stats['avg_mood']:.1f}/10. {stats['consistent_users']} people have been tracking mood for over a week straight!",
                        "hashtags": ["#УспіхиВетеранів", "#ПрогресВЛікуванні", "#VeteransSuccess", "#TreatmentProgress"],
                        "image_url": "https://images.pexels.com/photos/3760263/pexels-photo-3760263.jpeg"
                    }
                ]
                return stories
                
        except Exception as e:
            logger.error(f"Error getting success stories: {e}")
        
        return []
    
    async def get_educational_content(self) -> List[Dict[str, Any]]:
        """Get educational content about mental health"""
        educational = [
            {
                "type": "education",
                "content_uk": "🧠 ПТСР (посттравматичний стресовий розлад) - це нормальна реакція на ненормальні обставини. Симптоми включають флешбеки, кошмари, уникнення тригерів. Важливо знати: це лікується!",
                "content_en": "🧠 PTSD (Post-Traumatic Stress Disorder) is a normal reaction to abnormal circumstances. Symptoms include flashbacks, nightmares, trigger avoidance. Important to know: it's treatable!",
                "hashtags": ["#ПТСР", "#ОсвітаПроЗдоровя", "#ВетераниУкраїни", "#PTSD", "#HealthEducation"],
                "image_url": "https://images.pexels.com/photos/3825581/pexels-photo-3825581.jpeg"
            },
            {
                "type": "education",
                "content_uk": "💡 Депресія - це не слабкість, а медичний стан. Ознаки: постійна втома, втрата інтересу, зміни в апетиті та сні. Звертайтеся за допомогою - це ознака сили!",
                "content_en": "💡 Depression is not weakness, but a medical condition. Signs: persistent fatigue, loss of interest, changes in appetite and sleep. Seeking help is a sign of strength!",
                "hashtags": ["#Депресія", "#МентальнеЗдоровя", "#ПсихологічнаДопомога", "#Depression", "#MentalHealth"],
                "image_url": "https://images.pexels.com/photos/3771115/pexels-photo-3771115.jpeg"
            }
        ]
        
        return educational
    
    async def schedule_social_media_posts(self, content_list: List[Dict[str, Any]]):
        """Schedule posts to social media platforms"""
        try:
            for content in content_list:
                # Post to Facebook
                if self.facebook_token:
                    await self.post_to_facebook(content)
                
                # Post to Instagram
                if self.instagram_token:
                    await self.post_to_instagram(content)
                
                # Post to LinkedIn
                if self.linkedin_token:
                    await self.post_to_linkedin(content)
                
                # Small delay between posts
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Error scheduling social media posts: {e}")
    
    async def post_to_facebook(self, content: Dict[str, Any]):
        """Post content to Facebook page"""
        try:
            if not self.facebook_token:
                return
            
            post_text = content["content_uk"] + "\n\n" + " ".join(content["hashtags"])
            
            # Facebook Graph API call would go here
            logger.info(f"Would post to Facebook: {post_text[:50]}...")
            
        except Exception as e:
            logger.error(f"Error posting to Facebook: {e}")
    
    async def post_to_instagram(self, content: Dict[str, Any]):
        """Post content to Instagram"""
        try:
            if not self.instagram_token:
                return
            
            post_text = content["content_uk"] + "\n\n" + " ".join(content["hashtags"])
            
            # Instagram API call would go here
            logger.info(f"Would post to Instagram: {post_text[:50]}...")
            
        except Exception as e:
            logger.error(f"Error posting to Instagram: {e}")
    
    async def post_to_linkedin(self, content: Dict[str, Any]):
        """Post content to LinkedIn"""
        try:
            if not self.linkedin_token:
                return
            
            post_text = content["content_uk"] + "\n\n" + " ".join(content["hashtags"])
            
            # LinkedIn API call would go here
            logger.info(f"Would post to LinkedIn: {post_text[:50]}...")
            
        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
    
    async def process_referrals(self):
        """Process referral bonuses"""
        try:
            async with db_manager.pool.acquire() as conn:
                # Find completed referrals that haven't been awarded
                pending_referrals = await conn.fetch('''
                    SELECT r.id, r.referrer_id, r.referee_id
                    FROM referrals r
                    JOIN users referee ON r.referee_id = referee.user_id
                    WHERE r.bonus_awarded = false
                    AND referee.registration_date <= NOW() - INTERVAL '7 days'
                    AND referee.last_activity >= NOW() - INTERVAL '3 days'
                ''')
                
                for referral in pending_referrals:
                    # Award bonus to referrer
                    await self.award_referral_bonus(
                        referral['referrer_id'], 
                        referral['referee_id'],
                        referral['id']
                    )
                    
        except Exception as e:
            logger.error(f"Error processing referrals: {e}")
    
    async def award_referral_bonus(self, referrer_id: int, referee_id: int, referral_id: str):
        """Award referral bonus to user"""
        try:
            bonus_days = config.REFERRAL_BONUS_DAYS
            
            async with db_manager.pool.acquire() as conn:
                # Extend referrer's premium subscription
                await conn.execute('''
                    UPDATE users SET 
                        subscription_expires = COALESCE(subscription_expires, NOW()) + INTERVAL '%s days',
                        subscription_status = CASE 
                            WHEN subscription_status = 'free' THEN 'premium'
                            ELSE subscription_status
                        END
                    WHERE user_id = $1
                ''', bonus_days, referrer_id)
                
                # Mark referral as awarded
                await conn.execute('''
                    UPDATE referrals SET 
                        bonus_awarded = true,
                        bonus_days = $1
                    WHERE id = $2
                ''', bonus_days, referral_id)
                
                logger.info(f"Awarded {bonus_days} days premium to user {referrer_id} for referral")
                
        except Exception as e:
            logger.error(f"Error awarding referral bonus: {e}")
    
    async def generate_engagement_report(self) -> Dict[str, Any]:
        """Generate engagement analytics report"""
        try:
            async with db_manager.pool.acquire() as conn:
                # User engagement metrics
                engagement_stats = await conn.fetchrow('''
                    SELECT 
                        COUNT(*) as total_users,
                        COUNT(*) FILTER (WHERE last_activity >= NOW() - INTERVAL '1 day') as dau,
                        COUNT(*) FILTER (WHERE last_activity >= NOW() - INTERVAL '7 days') as wau,
                        COUNT(*) FILTER (WHERE last_activity >= NOW() - INTERVAL '30 days') as mau,
                        AVG(EXTRACT(EPOCH FROM (NOW() - registration_date))/86400) as avg_user_age_days
                    FROM users
                ''')
                
                # Feature usage
                feature_usage = await conn.fetchrow('''
                    SELECT 
                        COUNT(DISTINCT user_id) FILTER (WHERE timestamp >= NOW() - INTERVAL '7 days') as mood_users_week,
                        COUNT(*) FILTER (WHERE timestamp >= NOW() - INTERVAL '7 days') as mood_checkins_week,
                        (SELECT COUNT(DISTINCT user_id) FROM ai_chats WHERE timestamp >= NOW() - INTERVAL '7 days') as ai_users_week,
                        (SELECT COUNT(*) FROM ai_chats WHERE timestamp >= NOW() - INTERVAL '7 days') as ai_chats_week
                    FROM mood_checkins
                ''')
                
                # Retention metrics
                retention_stats = await conn.fetchrow('''
                    SELECT 
                        COUNT(*) FILTER (WHERE registration_date >= NOW() - INTERVAL '7 days' AND last_activity >= NOW() - INTERVAL '1 day') as new_user_retention_7d,
                        COUNT(*) FILTER (WHERE registration_date >= NOW() - INTERVAL '7 days') as new_users_7d
                    FROM users
                ''')
                
                report = {
                    "generated_at": datetime.now().isoformat(),
                    "user_metrics": dict(engagement_stats) if engagement_stats else {},
                    "feature_usage": dict(feature_usage) if feature_usage else {},
                    "retention": dict(retention_stats) if retention_stats else {}
                }
                
                # Calculate retention rate
                if retention_stats and retention_stats['new_users_7d'] > 0:
                    report["retention"]["retention_rate_7d"] = (
                        retention_stats['new_user_retention_7d'] / retention_stats['new_users_7d']
                    ) * 100
                
                return report
                
        except Exception as e:
            logger.error(f"Error generating engagement report: {e}")
            return {}
    
    async def send_marketing_campaigns(self):
        """Send targeted marketing campaigns"""
        try:
            # Re-engagement campaign for inactive users
            await self.send_reengagement_campaign()
            
            # Premium upgrade campaign
            await self.send_premium_campaign()
            
            # Referral reminder campaign
            await self.send_referral_campaign()
            
        except Exception as e:
            logger.error(f"Error sending marketing campaigns: {e}")
    
    async def send_reengagement_campaign(self):
        """Send re-engagement messages to inactive users"""
        try:
            async with db_manager.pool.acquire() as conn:
                inactive_users = await conn.fetch('''
                    SELECT user_id, first_name, language
                    FROM users 
                    WHERE last_activity BETWEEN NOW() - INTERVAL '14 days' AND NOW() - INTERVAL '7 days'
                    AND subscription_status != 'inactive'
                    LIMIT 100
                ''')
                
                reengagement_message_uk = """
🌟 Ми сумуємо за вами!

Привіт! Помітили, що ви давно не заходили до VetSupport AI. 

Ваше ментальне здоров'я важливе для нас. Повертайтесь - у нас є нові функції:
• Покращений ШІ-асистент
• Нові дихальні вправи
• Розширена база правової інформації

Ваша підтримка чекає на вас! 💙💛
                """
                
                logger.info(f"Would send re-engagement to {len(inactive_users)} users")
                
        except Exception as e:
            logger.error(f"Error in re-engagement campaign: {e}")
    
    async def send_premium_campaign(self):
        """Send premium upgrade campaign to eligible users"""
        try:
            async with db_manager.pool.acquire() as conn:
                eligible_users = await conn.fetch('''
                    SELECT u.user_id, u.first_name, u.language, us.ai_chats_count
                    FROM users u
                    JOIN user_stats us ON u.user_id = us.user_id
                    WHERE u.subscription_status = 'free'
                    AND us.ai_chats_count >= 10
                    AND u.last_activity >= NOW() - INTERVAL '3 days'
                    LIMIT 50
                ''')
                
                premium_message_uk = """
💎 Спеціальна пропозиція для вас!

Ви активно користуєтесь VetSupport AI - це чудово! 

Отримайте ще більше можливостей з Premium:
✨ Необмежені чати з ШІ
🎯 Персональні рекомендації
👨‍⚕️ Пріоритетний доступ до психологів

🎁 Перший тиждень безкоштовно!
                """
                
                logger.info(f"Would send premium campaign to {len(eligible_users)} users")
                
        except Exception as e:
            logger.error(f"Error in premium campaign: {e}")
    
    async def send_referral_campaign(self):
        """Send referral program reminders"""
        try:
            async with db_manager.pool.acquire() as conn:
                premium_users = await conn.fetch('''
                    SELECT u.user_id, u.first_name, u.language, u.referral_code
                    FROM users u
                    LEFT JOIN referrals r ON u.user_id = r.referrer_id
                    WHERE u.subscription_status IN ('premium', 'trial')
                    AND u.last_activity >= NOW() - INTERVAL '7 days'
                    GROUP BY u.user_id, u.first_name, u.language, u.referral_code
                    HAVING COUNT(r.id) < 3
                    LIMIT 30
                ''')
                
                referral_message_uk = """
🎁 Поділіться підтримкою з друзями!

Ваше реферальне посилання: 
https://t.me/VetSupportAI_bot?start={referral_code}

За кожного друга ви отримуєте:
• 1 тиждень Premium безкоштовно
• Ваш друг також отримує бонус

Разом ми сильніші! 💪
                """
                
                logger.info(f"Would send referral campaign to {len(premium_users)} users")
                
        except Exception as e:
            logger.error(f"Error in referral campaign: {e}")