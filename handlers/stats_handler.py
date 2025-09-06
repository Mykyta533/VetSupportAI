from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from datetime import datetime
import base64

from database.db_manager import db_manager
from services.stats_service import StatsService
from utils.keyboards import get_stats_keyboard, get_main_menu_keyboard
from utils.texts import get_text

router = Router()

@router.callback_query(F.data == "mood_stats")
async def mood_stats_menu(callback: CallbackQuery, language: str = "uk"):
    """Show mood statistics menu"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Check if user has mood data
    recent_moods = await db_manager.get_user_mood_history(user_id, 1)
    
    if not recent_moods:
        await callback.message.edit_text(
            get_text("no_mood_data", language),
            reply_markup=get_main_menu_keyboard(language)
        )
        return
    
    stats_text = get_text("stats_menu_text", language)
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_stats_keyboard(language)
    )

@router.callback_query(F.data == "stats_week")
async def weekly_stats(callback: CallbackQuery, language: str = "uk"):
    """Show weekly mood statistics"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    processing_msg = await callback.message.edit_text(get_text("generating_stats", language))
    
    try:
        stats_service = StatsService()
        
        # Get weekly data
        mood_data = await db_manager.get_user_mood_history(user_id, 7)
        
        if not mood_data:
            await callback.message.edit_text(
                get_text("no_weekly_data", language),
                reply_markup=get_stats_keyboard(language)
            )
            return
        
        # Generate weekly summary chart
        chart_base64 = await stats_service.generate_weekly_summary_chart(user_id, language)
        
        # Calculate weekly stats
        moods = [m['mood_level'] for m in mood_data]
        avg_mood = sum(moods) / len(moods)
        best_day = max(mood_data, key=lambda x: x['mood_level'])
        worst_day = min(mood_data, key=lambda x: x['mood_level'])
        
        stats_text = get_text("weekly_stats_text", language).format(
            days_tracked=len(mood_data),
            average_mood=f"{avg_mood:.1f}",
            best_mood=best_day['mood_level'],
            best_date=best_day['timestamp'].strftime('%d.%m'),
            worst_mood=worst_day['mood_level'],
            worst_date=worst_day['timestamp'].strftime('%d.%m')
        )
        
        await callback.message.edit_text(stats_text)
        
        # Send chart if available
        if chart_base64:
            chart_data = base64.b64decode(chart_base64)
            chart_file = BufferedInputFile(chart_data, filename="weekly_stats.png")
            await callback.message.answer_photo(
                chart_file,
                caption=get_text("weekly_chart_caption", language),
                reply_markup=get_stats_keyboard(language)
            )
        else:
            await callback.message.answer(
                get_text("chart_generation_failed", language),
                reply_markup=get_stats_keyboard(language)
            )
            
    except Exception as e:
        await callback.message.edit_text(
            get_text("stats_error", language),
            reply_markup=get_main_menu_keyboard(language)
        )

@router.callback_query(F.data == "stats_month")
async def monthly_stats(callback: CallbackQuery, language: str = "uk"):
    """Show monthly mood statistics"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    processing_msg = await callback.message.edit_text(get_text("generating_stats", language))
    
    try:
        stats_service = StatsService()
        
        # Generate monthly report
        report = await stats_service.generate_monthly_report(user_id, language)
        
        if not report:
            await callback.message.edit_text(
                get_text("no_monthly_data", language),
                reply_markup=get_stats_keyboard(language)
            )
            return
        
        stats = report.get("stats", {})
        
        # Build stats text
        stats_text = get_text("monthly_stats_text", language).format(
            total_checkins=stats.get("total_check_ins", 0),
            average_mood=f"{stats.get('average_mood', 0):.1f}",
            streak_days=stats.get("streak_days", 0),
            ai_chats=stats.get("ai_chats_count", 0),
            mood_trend=get_text(f'trend_{stats.get("mood_trend", "stable")}', language)
        )
        
        # Add insights
        insights = report.get("insights", [])
        if insights:
            stats_text += f"\n\n💡 {get_text('insights', language)}:\n"
            stats_text += "\n".join(f"• {insight}" for insight in insights)
        
        await callback.message.edit_text(stats_text)
        
        # Send mood chart if available
        if report.get("mood_chart"):
            chart_data = base64.b64decode(report["mood_chart"])
            chart_file = BufferedInputFile(chart_data, filename="monthly_mood.png")
            await callback.message.answer_photo(
                chart_file,
                caption=get_text("monthly_mood_chart", language)
            )
        
        # Send weekly summary chart if available  
        if report.get("weekly_chart"):
            weekly_data = base64.b64decode(report["weekly_chart"])
            weekly_file = BufferedInputFile(weekly_data, filename="weekly_summary.png")
            await callback.message.answer_photo(
                weekly_file,
                caption=get_text("weekly_summary_chart", language),
                reply_markup=get_stats_keyboard(language)
            )
        
        if not report.get("mood_chart") and not report.get("weekly_chart"):
            await callback.message.answer(
                get_text("charts_generation_failed", language),
                reply_markup=get_stats_keyboard(language)
            )
            
    except Exception as e:
        await callback.message.edit_text(
            get_text("stats_error", language),
            reply_markup=get_main_menu_keyboard(language)
        )

@router.callback_query(F.data == "stats_trends")
async def mood_trends(callback: CallbackQuery, language: str = "uk"):
    """Show mood trends analysis"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    processing_msg = await callback.message.edit_text(get_text("analyzing_trends", language))
    
    try:
        # Get mood data for trend analysis
        mood_data = await db_manager.get_user_mood_history(user_id, 30)
        
        if len(mood_data) < 5:
            await callback.message.edit_text(
                get_text("insufficient_data_for_trends", language),
                reply_markup=get_stats_keyboard(language)
            )
            return
        
        # Calculate trends
        moods = [m['mood_level'] for m in mood_data]
        
        # Recent vs older comparison
        recent_moods = moods[-7:] if len(moods) >= 7 else moods[-len(moods)//2:]
        older_moods = moods[:-7] if len(moods) >= 14 else moods[:len(moods)//2]
        
        recent_avg = sum(recent_moods) / len(recent_moods)
        older_avg = sum(older_moods) / len(older_moods) if older_moods else recent_avg
        
        # Determine trend
        if recent_avg > older_avg + 0.5:
            trend = "improving"
            trend_emoji = "📈"
        elif recent_avg < older_avg - 0.5:
            trend = "declining"  
            trend_emoji = "📉"
        else:
            trend = "stable"
            trend_emoji = "📊"
        
        # Calculate additional metrics
        mood_variance = sum((m - recent_avg) ** 2 for m in recent_moods) / len(recent_moods)
        stability = "stable" if mood_variance < 2 else "variable"
        
        # Best and worst periods
        best_period = max(mood_data, key=lambda x: x['mood_level'])
        worst_period = min(mood_data, key=lambda x: x['mood_level'])
        
        # Build trends text
        trends_text = get_text("trends_analysis", language).format(
            trend_emoji=trend_emoji,
            trend=get_text(f"trend_{trend}", language),
            recent_avg=f"{recent_avg:.1f}",
            older_avg=f"{older_avg:.1f}",
            stability=get_text(f"stability_{stability}", language),
            best_mood=best_period['mood_level'],
            best_date=best_period['timestamp'].strftime('%d.%m.%Y'),
            worst_mood=worst_period['mood_level'],
            worst_date=worst_period['timestamp'].strftime('%d.%m.%Y')
        )
        
        # Add trend-specific advice
        advice_key = f"trend_advice_{trend}"
        if hasattr(get_text, advice_key):
            trends_text += f"\n\n💡 {get_text('advice', language)}:\n"
            trends_text += get_text(advice_key, language)
        
        await callback.message.edit_text(
            trends_text,
            reply_markup=get_stats_keyboard(language)
        )
        
        # Generate and send trend chart
        stats_service = StatsService()
        chart_base64 = await stats_service.generate_mood_chart(user_id, 30, language)
        
        if chart_base64:
            chart_data = base64.b64decode(chart_base64)
            chart_file = BufferedInputFile(chart_data, filename="mood_trends.png")
            await callback.message.answer_photo(
                chart_file,
                caption=get_text("trends_chart_caption", language)
            )
            
    except Exception as e:
        await callback.message.edit_text(
            get_text("trends_error", language),
            reply_markup=get_stats_keyboard(language)
        )

@router.callback_query(F.data == "stats_detailed")
async def detailed_report(callback: CallbackQuery, language: str = "uk"):
    """Generate detailed statistics report"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    processing_msg = await callback.message.edit_text(get_text("generating_detailed_report", language))
    
    try:
        stats_service = StatsService()
        
        # Get comprehensive statistics
        user_stats = await stats_service.get_user_statistics(user_id)
        
        if not user_stats:
            await callback.message.edit_text(
                get_text("no_stats_data", language),
                reply_markup=get_stats_keyboard(language)
            )
            return
        
        # Build detailed report
        report_text = get_text("detailed_report_header", language)
        report_text += f"\n📅 {get_text('report_date', language)}: {datetime.now().strftime('%d.%m.%Y')}"
        
        # Mood tracking stats
        report_text += f"\n\n🧠 {get_text('mood_tracking', language)}:"
        report_text += f"\n• {get_text('total_checkins', language)}: {user_stats.get('total_check_ins', 0)}"
        report_text += f"\n• {get_text('average_mood', language)}: {user_stats.get('average_mood', 0):.1f}/10"
        report_text += f"\n• {get_text('current_streak', language)}: {user_stats.get('streak_days', 0)} {get_text('days', language)}"
        report_text += f"\n• {get_text('mood_trend', language)}: {get_text(f'trend_{user_stats.get("mood_trend", "stable")}', language)}"
        
        # AI Chat stats
        report_text += f"\n\n🤖 {get_text('ai_interactions', language)}:"
        report_text += f"\n• {get_text('total_chats', language)}: {user_stats.get('ai_chats_count', 0)}"
        report_text += f"\n• {get_text('voice_chats', language)}: {user_stats.get('voice_chats', 0)}"
        
        # Additional metrics
        if user_stats.get('recent_average'):
            report_text += f"\n\n📊 {get_text('recent_metrics', language)}:"
            report_text += f"\n• {get_text('recent_average', language)}: {user_stats['recent_average']:.1f}/10"
            
            if user_stats.get('mood_variance'):
                stability = "stable" if user_stats['mood_variance'] < 2 else "variable"
                report_text += f"\n• {get_text('mood_stability', language)}: {get_text(f'stability_{stability}', language)}"
        
        # Best and worst days
        if user_stats.get('best_mood_day'):
            best_day = user_stats['best_mood_day']
            report_text += f"\n\n🌟 {get_text('best_mood_day', language)}:"
            report_text += f"\n• {get_text('date', language)}: {best_day['timestamp'].strftime('%d.%m.%Y')}"
            report_text += f"\n• {get_text('mood', language)}: {best_day['mood_level']}/10"
            if best_day.get('note'):
                report_text += f"\n• {get_text('note', language)}: {best_day['note'][:100]}..."
        
        await callback.message.edit_text(
            report_text,
            reply_markup=get_stats_keyboard(language)
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("detailed_report_error", language),
            reply_markup=get_stats_keyboard(language)
        )
