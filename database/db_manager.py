import asyncio
import asyncpg
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from config import config
from database.models import *

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.pool = None
    
    async def init_database(self):
        """Initialize database connection pool and create tables"""
        try:
            self.pool = await asyncpg.create_pool(
                config.DATABASE_URL,
                min_size=1,
                max_size=10,
                server_settings={
                    'application_name': 'VetSupport AI Bot',
                }
            )
            
            await self.create_tables()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def create_tables(self):
        """Create all necessary database tables"""
        async with self.pool.acquire() as conn:
            # Users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(32),
                    first_name VARCHAR(64),
                    last_name VARCHAR(64),
                    language VARCHAR(10) DEFAULT 'uk',
                    role VARCHAR(20) DEFAULT 'user',
                    subscription_status VARCHAR(20) DEFAULT 'free',
                    subscription_expires TIMESTAMP,
                    referral_code VARCHAR(16) UNIQUE,
                    referred_by BIGINT,
                    is_veteran BOOLEAN DEFAULT false,
                    registration_date TIMESTAMP DEFAULT NOW(),
                    last_activity TIMESTAMP DEFAULT NOW(),
                    privacy_accepted BOOLEAN DEFAULT false,
                    terms_accepted BOOLEAN DEFAULT false,
                    phone_number VARCHAR(20),
                    email VARCHAR(100),
                    emergency_contact VARCHAR(100)
                )
            ''')
            
            # Mood check-ins table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS mood_checkins (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id BIGINT REFERENCES users(user_id),
                    mood_level INTEGER CHECK (mood_level >= 1 AND mood_level <= 10),
                    note TEXT,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    ai_analysis JSONB,
                    recommended_actions TEXT[]
                )
            ''')
            
            # AI Chats table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS ai_chats (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id BIGINT REFERENCES users(user_id),
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    model_used VARCHAR(20) DEFAULT 'gemini',
                    is_voice BOOLEAN DEFAULT false,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    sentiment_score FLOAT,
                    crisis_flag BOOLEAN DEFAULT false
                )
            ''')
            
            # Recommendations table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS recommendations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(200) NOT NULL,
                    content TEXT NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    language VARCHAR(10) DEFAULT 'uk',
                    target_mood INTEGER[],
                    difficulty_level INTEGER DEFAULT 1,
                    duration_minutes INTEGER DEFAULT 0,
                    media_url TEXT,
                    created_date TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Consultations table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS consultations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id BIGINT REFERENCES users(user_id),
                    psychologist_id BIGINT,
                    consultation_type VARCHAR(20) DEFAULT 'text',
                    status VARCHAR(20) DEFAULT 'scheduled',
                    scheduled_time TIMESTAMP,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    notes TEXT,
                    rating INTEGER,
                    feedback TEXT,
                    cost INTEGER DEFAULT 0
                )
            ''')
            
            # Legal documents table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS legal_documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(300) NOT NULL,
                    content TEXT NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    language VARCHAR(10) DEFAULT 'uk',
                    last_updated TIMESTAMP DEFAULT NOW(),
                    source_url TEXT,
                    is_template BOOLEAN DEFAULT false,
                    tags TEXT[]
                )
            ''')
            
            # Telemedicine appointments table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS telemedicine_appointments (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id BIGINT REFERENCES users(user_id),
                    doctor_name VARCHAR(100) NOT NULL,
                    specialization VARCHAR(100) NOT NULL,
                    appointment_date DATE,
                    appointment_time TIME,
                    status VARCHAR(20) DEFAULT 'pending',
                    appointment_url TEXT,
                    notes TEXT,
                    cost INTEGER DEFAULT 0
                )
            ''')
            
            # User statistics table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id BIGINT PRIMARY KEY REFERENCES users(user_id),
                    total_check_ins INTEGER DEFAULT 0,
                    average_mood FLOAT DEFAULT 0.0,
                    streak_days INTEGER DEFAULT 0,
                    ai_chats_count INTEGER DEFAULT 0,
                    consultations_count INTEGER DEFAULT 0,
                    recommendations_completed INTEGER DEFAULT 0,
                    last_check_in TIMESTAMP,
                    mood_trend VARCHAR(20) DEFAULT 'stable'
                )
            ''')
            
            # Referral system table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    referrer_id BIGINT REFERENCES users(user_id),
                    referee_id BIGINT REFERENCES users(user_id),
                    referral_date TIMESTAMP DEFAULT NOW(),
                    bonus_awarded BOOLEAN DEFAULT false,
                    bonus_days INTEGER DEFAULT 0
                )
            ''')
            
            # Marketing campaigns table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS marketing_campaigns (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(200) NOT NULL,
                    content TEXT NOT NULL,
                    campaign_type VARCHAR(50) DEFAULT 'tip',
                    target_channels TEXT[],
                    scheduled_time TIMESTAMP,
                    sent_time TIMESTAMP,
                    engagement_stats JSONB DEFAULT '{}',
                    is_active BOOLEAN DEFAULT true
                )
            ''')
            
            # Create indexes for better performance
            await self.create_indexes(conn)
    
    async def create_indexes(self, conn):
        """Create database indexes for optimization"""
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code)',
            'CREATE INDEX IF NOT EXISTS idx_mood_checkins_user_id ON mood_checkins(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_mood_checkins_timestamp ON mood_checkins(timestamp DESC)',
            'CREATE INDEX IF NOT EXISTS idx_ai_chats_user_id ON ai_chats(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_ai_chats_timestamp ON ai_chats(timestamp DESC)',
            'CREATE INDEX IF NOT EXISTS idx_consultations_user_id ON consultations(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_telemedicine_user_id ON telemedicine_appointments(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_legal_category ON legal_documents(category)',
            'CREATE INDEX IF NOT EXISTS idx_legal_language ON legal_documents(language)'
        ]
        
        for index_sql in indexes:
            try:
                await conn.execute(index_sql)
            except Exception as e:
                logger.warning(f"Index creation failed: {e}")
    
    # User management methods
    async def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO users (
                        user_id, username, first_name, last_name, language, role,
                        subscription_status, referral_code, referred_by, is_veteran,
                        privacy_accepted, terms_accepted
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        last_activity = NOW()
                ''', user.user_id, user.username, user.first_name, user.last_name,
                user.language, user.role.value, user.subscription_status.value,
                user.referral_code, user.referred_by, user.is_veteran,
                user.privacy_accepted, user.terms_accepted)
                
                # Create user stats entry
                await conn.execute('''
                    INSERT INTO user_stats (user_id) VALUES ($1)
                    ON CONFLICT (user_id) DO NOTHING
                ''', user.user_id)
                
                return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    'SELECT * FROM users WHERE user_id = $1', user_id
                )
                
                if row:
                    user = User(
                        user_id=row['user_id'],
                        username=row['username'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        language=row['language'],
                        role=UserRole(row['role'])
                    )
                    user.subscription_status = SubscriptionStatus(row['subscription_status'])
                    user.subscription_expires = row['subscription_expires']
                    user.referral_code = row['referral_code']
                    user.referred_by = row['referred_by']
                    user.is_veteran = row['is_veteran']
                    user.registration_date = row['registration_date']
                    user.last_activity = row['last_activity']
                    user.privacy_accepted = row['privacy_accepted']
                    user.terms_accepted = row['terms_accepted']
                    user.phone_number = row['phone_number']
                    user.email = row['email']
                    user.emergency_contact = row['emergency_contact']
                    
                    return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
        
        return None
    
    # Mood check-in methods
    async def create_mood_checkin(self, checkin: MoodCheckIn) -> bool:
        """Create a new mood check-in"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO mood_checkins (user_id, mood_level, note, ai_analysis, recommended_actions)
                    VALUES ($1, $2, $3, $4, $5)
                ''', checkin.user_id, checkin.mood_level, checkin.note, 
                json.dumps(checkin.ai_analysis), checkin.recommended_actions)
                
                # Update user stats
                await self.update_mood_stats(checkin.user_id, checkin.mood_level)
                
                return True
        except Exception as e:
            logger.error(f"Error creating mood check-in: {e}")
            return False
    
    async def get_user_mood_history(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get user's mood history for the specified number of days"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch('''
                    SELECT mood_level, note, timestamp
                    FROM mood_checkins
                    WHERE user_id = $1 AND timestamp >= $2
                    ORDER BY timestamp DESC
                ''', user_id, datetime.now() - timedelta(days=days))
                
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting mood history: {e}")
            return []
    
    async def update_mood_stats(self, user_id: int, new_mood: int):
        """Update user's mood statistics"""
        try:
            async with self.pool.acquire() as conn:
                # Get current stats
                stats = await conn.fetchrow(
                    'SELECT * FROM user_stats WHERE user_id = $1', user_id
                )
                
                if stats:
                    total_checkins = stats['total_check_ins'] + 1
                    current_avg = stats['average_mood']
                    
                    # Calculate new average
                    new_avg = ((current_avg * (total_checkins - 1)) + new_mood) / total_checkins
                    
                    # Calculate streak
                    last_checkin = stats['last_check_in']
                    streak = stats['streak_days']
                    
                    if last_checkin:
                        days_diff = (datetime.now() - last_checkin).days
                        if days_diff == 1:
                            streak += 1
                        elif days_diff > 1:
                            streak = 1
                    else:
                        streak = 1
                    
                    await conn.execute('''
                        UPDATE user_stats SET
                            total_check_ins = $1,
                            average_mood = $2,
                            streak_days = $3,
                            last_check_in = NOW()
                        WHERE user_id = $4
                    ''', total_checkins, new_avg, streak, user_id)
        except Exception as e:
            logger.error(f"Error updating mood stats: {e}")
    
    # AI Chat methods
    async def save_ai_chat(self, chat: AIChat) -> bool:
        """Save AI chat interaction"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO ai_chats (user_id, message, response, model_used, is_voice, sentiment_score, crisis_flag)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                ''', chat.user_id, chat.message, chat.response, chat.model_used, 
                chat.is_voice, chat.sentiment_score, chat.crisis_flag)
                
                # Update user stats
                await conn.execute('''
                    UPDATE user_stats SET ai_chats_count = ai_chats_count + 1
                    WHERE user_id = $1
                ''', chat.user_id)
                
                return True
        except Exception as e:
            logger.error(f"Error saving AI chat: {e}")
            return False
    
    # Recommendations methods
    async def get_recommendations(self, category: str = None, language: str = "uk", 
                                 mood_level: int = None) -> List[Dict]:
        """Get recommendations based on criteria"""
        try:
            async with self.pool.acquire() as conn:
                query = 'SELECT * FROM recommendations WHERE language = $1'
                params = [language]
                
                if category:
                    query += ' AND category = $2'
                    params.append(category)
                
                if mood_level:
                    query += f' AND ${"3" if category else "2"} = ANY(target_mood)'
                    params.append(mood_level)
                
                query += ' ORDER BY created_date DESC'
                
                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    # Legal documents methods
    async def get_legal_documents(self, category: str = None, language: str = "uk") -> List[Dict]:
        """Get legal documents"""
        try:
            async with self.pool.acquire() as conn:
                if category:
                    rows = await conn.fetch('''
                        SELECT * FROM legal_documents 
                        WHERE category = $1 AND language = $2
                        ORDER BY last_updated DESC
                    ''', category, language)
                else:
                    rows = await conn.fetch('''
                        SELECT * FROM legal_documents 
                        WHERE language = $1
                        ORDER BY category, last_updated DESC
                    ''', language)
                
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting legal documents: {e}")
            return []
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()

# Global database manager instance
db_manager = DatabaseManager()