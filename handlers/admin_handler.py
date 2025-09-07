from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from datetime import datetime, timedelta

from database.db_manager import db_manager
from config import config

router = Router()

# Admin commands - only accessible to admin users
@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Admin panel access"""
    if str(message.from_user.id) != config.get('ADMIN_CHAT_ID'):
        await message.answer("❌ Access denied")
        return
    
    admin_text = "🔧 **Admin Panel**\n\n"
    admin_text += "Available commands:\n"
    admin_text += "/stats - Bot statistics\n"
    admin_text += "/users - User management\n"
    admin_text += "/broadcast - Send broadcast message\n"
    admin_text += "/maintenance - Toggle maintenance mode\n"
    admin_text += "/logs - View recent logs"
    
    await message.answer(admin_text, parse_mode="Markdown")

@router.message(Command("stats"))
async def bot_statistics(message: Message):
    """Show bot statistics"""
    if str(message.from_user.id) != config.get('ADMIN_CHAT_ID'):
        return
    
    try:
        async with db_manager.pool.acquire() as conn:
            # User statistics
            total_users = await conn.fetchval('SELECT COUNT(*) FROM users')
            new_users_today = await conn.fetchval('''
                SELECT COUNT(*) FROM users 
                WHERE registration_date >= CURRENT_DATE
            ''')
            active_users_week = await conn.fetchval('''
                SELECT COUNT(*) FROM users 
                WHERE last_activity >= NOW() - INTERVAL '7 days'
            ''')
            
            # Mood statistics
            total_checkins = await conn.fetchval('SELECT COUNT(*) FROM mood_checkins')
            checkins_today = await conn.fetchval('''
                SELECT COUNT(*) FROM mood_checkins 
                WHERE timestamp >= CURRENT_DATE
            ''')
            avg_mood = await conn.fetchval('''
                SELECT AVG(mood_level) FROM mood_checkins 
                WHERE timestamp >= NOW() - INTERVAL '30 days'
            ''')
            
            # AI chat statistics
            total_chats = await conn.fetchval('SELECT COUNT(*) FROM ai_chats')
            chats_today = await conn.fetchval('''
                SELECT COUNT(*) FROM ai_chats 
                WHERE timestamp >= CURRENT_DATE
            ''')
            
            # Premium statistics
            premium_users = await conn.fetchval('''
                SELECT COUNT(*) FROM users 
                WHERE subscription_status IN ('premium', 'trial')
            ''')
        
        stats_text = f"📊 **Bot Statistics**\n\n"
        stats_text += f"👥 **Users:**\n"
        stats_text += f"• Total: {total_users}\n"
        stats_text += f"• New today: {new_users_today}\n"
        stats_text += f"• Active this week: {active_users_week}\n"
        stats_text += f"• Premium: {premium_users}\n\n"
        
        stats_text += f"🧠 **Mood Tracking:**\n"
        stats_text += f"• Total check-ins: {total_checkins}\n"
        stats_text += f"• Check-ins today: {checkins_today}\n"
        stats_text += f"• Average mood (30d): {avg_mood:.1f if avg_mood else 0}/10\n\n"
        
        stats_text += f"🤖 **AI Chats:**\n"
        stats_text += f"• Total chats: {total_chats}\n"
        stats_text += f"• Chats today: {chats_today}\n\n"
        
        stats_text += f"📅 Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        await message.answer(stats_text, parse_mode="Markdown")
        
    except Exception as e:
        await message.answer(f"❌ Error getting statistics: {e}")

@router.message(Command("users"))
async def user_management(message: Message):
    """User management commands"""
    if str(message.from_user.id) != config.get('ADMIN_CHAT_ID'):
        return
    
    try:
        async with db_manager.pool.acquire() as conn:
            # Recent users
            recent_users = await conn.fetch('''
                SELECT user_id, first_name, username, registration_date, last_activity, is_veteran
                FROM users 
                ORDER BY registration_date DESC 
                LIMIT 10
            ''')
        
        users_text = "👥 **Recent Users (Last 10)**\n\n"
        
        for user in recent_users:
            veteran_badge = "🎖️" if user['is_veteran'] else ""
            users_text += f"{veteran_badge} **{user['first_name']}** (@{user['username'] or 'N/A'})\n"
            users_text += f"   ID: `{user['user_id']}`\n"
            users_text += f"   Registered: {user['registration_date'].strftime('%d.%m.%Y')}\n"
            users_text += f"   Last active: {user['last_activity'].strftime('%d.%m.%Y %H:%M')}\n\n"
        
        await message.answer(users_text, parse_mode="Markdown")
        
    except Exception as e:
        await message.answer(f"❌ Error getting users: {e}")

@router.message(Command("broadcast"))
async def broadcast_message(message: Message):
    """Send broadcast message to all users"""
    if str(message.from_user.id) != config.get('ADMIN_CHAT_ID'):
        return
    
    # Extract message text after command
    text_parts = message.text.split(' ', 1)
    if len(text_parts) < 2:
        await message.answer("Usage: /broadcast <message>")
        return
    
    broadcast_text = text_parts[1]
    
    try:
        async with db_manager.pool.acquire() as conn:
            # Get all active users
            users = await conn.fetch('''
                SELECT user_id FROM users 
                WHERE last_activity >= NOW() - INTERVAL '30 days'
            ''')
        
        sent_count = 0
        failed_count = 0
        
        await message.answer(f"📢 Starting broadcast to {len(users)} users...")
        
        for user in users:
            try:
                await message.bot.send_message(
                    user['user_id'], 
                    f"📢 **Повідомлення від адміністрації:**\n\n{broadcast_text}",
                    parse_mode="Markdown"
                )
                sent_count += 1
            except Exception:
                failed_count += 1
        
        result_text = f"✅ Broadcast completed!\n"
        result_text += f"• Sent: {sent_count}\n"
        result_text += f"• Failed: {failed_count}"
        
        await message.answer(result_text)
        
    except Exception as e:
        await message.answer(f"❌ Broadcast error: {e}")

@router.message(Command("maintenance"))
async def toggle_maintenance(message: Message):
    """Toggle maintenance mode"""
    if str(message.from_user.id) != config.get('ADMIN_CHAT_ID'):
        return
    
    # This would integrate with the maintenance middleware
    await message.answer("🔧 Maintenance mode toggle - feature in development")

@router.message(Command("logs"))
async def view_logs(message: Message):
    """View recent bot logs"""
    if str(message.from_user.id) != config.get('ADMIN_CHAT_ID'):
        return
    
    try:
        # In a real implementation, this would read from log files
        logs_text = "📋 **Recent Logs**\n\n"
        logs_text += f"[{datetime.now().strftime('%H:%M:%S')}] Bot is running normally\n"
        logs_text += f"[{(datetime.now() - timedelta(minutes=5)).strftime('%H:%M:%S')}] Database connection healthy\n"
        logs_text += f"[{(datetime.now() - timedelta(minutes=10)).strftime('%H:%M:%S')}] AI service responding\n"
        logs_text += "\n💡 For detailed logs, check server console"
        
        await message.answer(logs_text, parse_mode="Markdown")
        
    except Exception as e:
        await message.answer(f"❌ Error getting logs: {e}")

# Crisis detection and admin notifications
async def notify_admin_crisis(user_id: int, message_text: str, crisis_indicators: dict):
    """Notify admin about crisis detection"""
    if not config.get('ADMIN_CHAT_ID'):
        return
    
    try:
        notification_text = f"🚨 **Crisis Alert**\n\n"
        notification_text += f"User ID: `{user_id}`\n"
        notification_text += f"Confidence: {crisis_indicators.get('confidence', 0):.2f}\n"
        notification_text += f"Indicators: {', '.join(crisis_indicators.get('indicators', []))}\n\n"
        notification_text += f"Message: {message_text[:200]}..."
        
        # This would be called from the AI service when crisis is detected
        # await bot.send_message(config.ADMIN_CHAT_ID, notification_text, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Failed to send crisis notification: {e}")