import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO
import base64

from database.db_manager import db_manager
from config import config

logger = logging.getLogger(__name__)

class StatsService:
    def __init__(self):
        # Set up matplotlib for non-interactive use
        plt.switch_backend('Agg')
        sns.set_style("whitegrid")
        
    async def generate_mood_chart(self, user_id: int, period_days: int = 30, 
                                 language: str = "uk") -> Optional[str]:
        """
        Generate mood chart for user
        Returns base64 encoded image
        """
        try:
            # Get mood data
            mood_data = await db_manager.get_user_mood_history(user_id, period_days)
            
            if not mood_data:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(mood_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Create figure
            plt.figure(figsize=(12, 6))
            
            # Plot mood line
            plt.plot(df['timestamp'], df['mood_level'], 
                    marker='o', markersize=6, linewidth=2, color='#3B82F6')
            
            # Add trend line
            if len(df) > 3:
                z = np.polyfit(range(len(df)), df['mood_level'], 1)
                p = np.poly1d(z)
                plt.plot(df['timestamp'], p(range(len(df))), 
                        "--", alpha=0.7, color='#EF4444', linewidth=2)
            
            # Customize chart
            plt.title(self._get_chart_title("mood_chart", language), 
                     fontsize=16, fontweight='bold', pad=20)
            plt.xlabel(self._get_chart_title("date", language), fontsize=12)
            plt.ylabel(self._get_chart_title("mood_level", language), fontsize=12)
            
            # Set y-axis limits and ticks
            plt.ylim(0, 11)
            plt.yticks(range(1, 11))
            
            # Format x-axis
            if period_days <= 7:
                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
                plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            elif period_days <= 30:
                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
                plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator())
            else:
                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
                plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            
            plt.xticks(rotation=45)
            
            # Add mood zones
            plt.axhspan(1, 3, alpha=0.1, color='red', label=self._get_chart_title("low_mood", language))
            plt.axhspan(4, 7, alpha=0.1, color='yellow', label=self._get_chart_title("medium_mood", language))
            plt.axhspan(8, 10, alpha=0.1, color='green', label=self._get_chart_title("good_mood", language))
            
            plt.legend()
            plt.tight_layout()
            
            # Save to bytes
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Encode to base64
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            plt.close()
            return img_str
            
        except Exception as e:
            logger.error(f"Error generating mood chart: {e}")
            return None
    
    async def generate_weekly_summary_chart(self, user_id: int, language: str = "uk") -> Optional[str]:
        """
        Generate weekly mood summary chart
        """
        try:
            # Get last 7 days of data
            mood_data = await db_manager.get_user_mood_history(user_id, 7)
            
            if not mood_data:
                return None
            
            # Process data by day
            df = pd.DataFrame(mood_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            
            # Get daily averages
            daily_avg = df.groupby('date')['mood_level'].mean().reset_index()
            daily_avg = daily_avg.sort_values('date')
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Chart 1: Daily mood bars
            colors = ['#EF4444' if mood <= 3 else '#F59E0B' if mood <= 7 else '#10B981' 
                     for mood in daily_avg['mood_level']]
            
            ax1.bar(daily_avg['date'], daily_avg['mood_level'], color=colors, alpha=0.7)
            ax1.set_title(self._get_chart_title("weekly_mood", language), fontsize=14, fontweight='bold')
            ax1.set_ylabel(self._get_chart_title("mood_level", language))
            ax1.set_ylim(0, 10)
            ax1.grid(True, alpha=0.3)
            
            # Chart 2: Mood distribution pie
            mood_ranges = {
                self._get_chart_title("low_mood", language): len([m for m in daily_avg['mood_level'] if m <= 3]),
                self._get_chart_title("medium_mood", language): len([m for m in daily_avg['mood_level'] if 4 <= m <= 7]),
                self._get_chart_title("good_mood", language): len([m for m in daily_avg['mood_level'] if m >= 8])
            }
            
            # Filter out zero values
            mood_ranges = {k: v for k, v in mood_ranges.items() if v > 0}
            
            if mood_ranges:
                ax2.pie(mood_ranges.values(), labels=mood_ranges.keys(), autopct='%1.1f%%',
                       colors=['#EF4444', '#F59E0B', '#10B981'])
                ax2.set_title(self._get_chart_title("mood_distribution", language), fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            # Save to bytes
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Encode to base64
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            plt.close()
            return img_str
            
        except Exception as e:
            logger.error(f"Error generating weekly summary: {e}")
            return None
    
    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive user statistics
        """
        try:
            async with db_manager.pool.acquire() as conn:
                # Get basic stats
                stats_row = await conn.fetchrow(
                    'SELECT * FROM user_stats WHERE user_id = $1', user_id
                )
                
                if not stats_row:
                    return {}
                
                # Get recent mood data
                recent_moods = await db_manager.get_user_mood_history(user_id, 30)
                
                # Calculate additional metrics
                stats = dict(stats_row)
                
                if recent_moods:
                    moods = [m['mood_level'] for m in recent_moods]
                    stats['recent_average'] = sum(moods) / len(moods)
                    stats['mood_variance'] = np.var(moods)
                    stats['best_mood_day'] = max(recent_moods, key=lambda x: x['mood_level'])
                    stats['worst_mood_day'] = min(recent_moods, key=lambda x: x['mood_level'])
                    
                    # Calculate trend
                    if len(moods) >= 5:
                        recent_5 = moods[-5:]
                        older_5 = moods[-10:-5] if len(moods) >= 10 else moods[:-5]
                        
                        if older_5:
                            recent_avg = sum(recent_5) / len(recent_5)
                            older_avg = sum(older_5) / len(older_5)
                            
                            if recent_avg > older_avg + 0.5:
                                stats['mood_trend'] = 'improving'
                            elif recent_avg < older_avg - 0.5:
                                stats['mood_trend'] = 'declining'
                            else:
                                stats['mood_trend'] = 'stable'
                
                # Get AI chat statistics
                ai_chat_stats = await conn.fetchrow('''
                    SELECT COUNT(*) as total_chats,
                           COUNT(*) FILTER (WHERE is_voice = true) as voice_chats,
                           AVG(sentiment_score) as avg_sentiment
                    FROM ai_chats 
                    WHERE user_id = $1 AND timestamp >= $2
                ''', user_id, datetime.now() - timedelta(days=30))
                
                if ai_chat_stats:
                    stats.update(dict(ai_chat_stats))
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {}
    
    async def generate_monthly_report(self, user_id: int, language: str = "uk") -> Dict[str, Any]:
        """
        Generate comprehensive monthly report
        """
        try:
            stats = await self.get_user_statistics(user_id)
            
            if not stats:
                return {}
            
            # Get mood data for the month
            mood_data = await db_manager.get_user_mood_history(user_id, 30)
            
            # Generate charts
            mood_chart = await self.generate_mood_chart(user_id, 30, language)
            weekly_chart = await self.generate_weekly_summary_chart(user_id, language)
            
            # Calculate insights
            insights = []
            
            if stats.get('mood_trend') == 'improving':
                insights.append(self._get_insight("improving_trend", language))
            elif stats.get('mood_trend') == 'declining':
                insights.append(self._get_insight("declining_trend", language))
            else:
                insights.append(self._get_insight("stable_trend", language))
            
            if stats.get('streak_days', 0) >= 7:
                insights.append(self._get_insight("good_streak", language).format(
                    days=stats['streak_days']
                ))
            
            if stats.get('average_mood', 0) >= 7:
                insights.append(self._get_insight("high_average", language))
            
            return {
                "stats": stats,
                "mood_chart": mood_chart,
                "weekly_chart": weekly_chart,
                "insights": insights,
                "mood_data_count": len(mood_data),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {e}")
            return {}
    
    def _get_chart_title(self, key: str, language: str) -> str:
        """Get localized chart titles"""
        titles = {
            "uk": {
                "mood_chart": "Динаміка настрою",
                "date": "Дата",
                "mood_level": "Рівень настрою",
                "weekly_mood": "Настрій за тиждень",
                "mood_distribution": "Розподіл настрою",
                "low_mood": "Низький (1-3)",
                "medium_mood": "Середній (4-7)",
                "good_mood": "Хороший (8-10)"
            },
            "en": {
                "mood_chart": "Mood Dynamics",
                "date": "Date",
                "mood_level": "Mood Level",
                "weekly_mood": "Weekly Mood",
                "mood_distribution": "Mood Distribution",
                "low_mood": "Low (1-3)",
                "medium_mood": "Medium (4-7)",
                "good_mood": "Good (8-10)"
            }
        }
        
        return titles.get(language, titles["uk"]).get(key, key)
    
    def _get_insight(self, key: str, language: str) -> str:
        """Get localized insights"""
        insights = {
            "uk": {
                "improving_trend": "📈 Ваш настрій покращується! Продовжуйте в тому ж дусі.",
                "declining_trend": "📉 Помічаю зниження настрою. Можливо, варто звернутися за підтримкою.",
                "stable_trend": "📊 Ваш настрій стабільний. Це хороший знак!",
                "good_streak": "🔥 Чудово! Ви ведете щоденник настрою вже {days} днів поспіль!",
                "high_average": "😊 Ваш середній настрій дуже хороший - продовжуйте!"
            },
            "en": {
                "improving_trend": "📈 Your mood is improving! Keep up the good work.",
                "declining_trend": "📉 I notice a decline in mood. Maybe it's worth seeking support.",
                "stable_trend": "📊 Your mood is stable. That's a good sign!",
                "good_streak": "🔥 Great! You've been tracking your mood for {days} days straight!",
                "high_average": "😊 Your average mood is very good - keep it up!"
            }
        }
        
        return insights.get(language, insights["uk"]).get(key, key)