from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import json
import random

from database.db_manager import db_manager
from utils.keyboards import get_recommendations_keyboard, get_main_menu_keyboard
from utils.texts import get_text

router = Router()

@router.callback_query(F.data == "recommendations")
async def recommendations_menu(callback: CallbackQuery, language: str = "uk"):
    """Show recommendations menu"""
    await callback.answer()
    
    menu_text = get_text("recommendations_menu", language, default="Оберіть тип рекомендацій:")
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=get_recommendations_keyboard(language)
    )

@router.callback_query(F.data.startswith("rec_"))
async def show_recommendations(callback: CallbackQuery, language: str = "uk"):
    """Show specific category recommendations"""
    await callback.answer()
    
    category = callback.data.split("_")[1]  # breathing, physical, meditation, etc.
    user_id = callback.from_user.id
    
    # Get user's recent mood for personalized recommendations
    recent_moods = await db_manager.get_user_mood_history(user_id, 3)
    current_mood = None
    if recent_moods:
        current_mood = recent_moods[0]["mood_level"]
    
    # Load recommendations from catalog
    try:
        with open("catalog.json", "r", encoding="utf-8") as f:
            catalog = json.load(f)
        
        recommendations = catalog.get("recommendations", {}).get(f"{category}_exercises", [])
        
        if not recommendations:
            await callback.message.edit_text(
                get_text("no_recommendations", language, default="Рекомендації не знайдено"),
                reply_markup=get_recommendations_keyboard(language)
            )
            return
        
        # Filter by mood if available
        if current_mood:
            suitable_recs = [r for r in recommendations 
                           if current_mood in r.get("target_mood", [])]
            if suitable_recs:
                recommendations = suitable_recs
        
        # Select random recommendation
        recommendation = random.choice(recommendations)
        
        # Format recommendation text
        title = recommendation["title"].get(language, recommendation["title"]["uk"])
        description = recommendation["description"].get(language, recommendation["description"]["uk"])
        instructions = recommendation["instructions"].get(language, recommendation["instructions"]["uk"])
        
        rec_text = f"💡 **{title}**\n\n"
        rec_text += f"📝 {description}\n\n"
        rec_text += f"📋 **{get_text('instructions', language, default='Інструкції')}:**\n"
        
        for i, instruction in enumerate(instructions, 1):
            rec_text += f"{i}. {instruction}\n"
        
        # Add metadata
        duration = recommendation.get("duration_minutes", 0)
        difficulty = recommendation.get("difficulty", 1)
        
        if duration > 0:
            rec_text += f"\n⏱ {get_text('duration', language, default='Тривалість')}: {duration} {get_text('minutes', language, default='хвилин')}"
        
        difficulty_text = get_text(f"difficulty_{difficulty}", language, default=f"Рівень {difficulty}")
        rec_text += f"\n📊 {get_text('difficulty', language, default='Складність')}: {difficulty_text}"
        
        # Create keyboard with options
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("another_recommendation", language, default="Інша рекомендація"),
                    callback_data=f"rec_{category}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("mark_completed", language, default="Позначити виконаним"),
                    callback_data=f"complete_{recommendation['id']}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back_to_recommendations", language, default="Назад до рекомендацій"),
                    callback_data="recommendations"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back_to_menu", language),
                    callback_data="main_menu"
                )
            ]
        ])
        
        await callback.message.edit_text(
            rec_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("recommendations_error", language, default="Помилка завантаження рекомендацій"),
            reply_markup=get_main_menu_keyboard(language)
        )

@router.callback_query(F.data.startswith("complete_"))
async def mark_recommendation_completed(callback: CallbackQuery, language: str = "uk"):
    """Mark recommendation as completed"""
    await callback.answer()
    
    recommendation_id = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    try:
        # Update user stats
        async with db_manager.pool.acquire() as conn:
            await conn.execute('''
                UPDATE user_stats 
                SET recommendations_completed = recommendations_completed + 1
                WHERE user_id = $1
            ''', user_id)
        
        completion_text = get_text("recommendation_completed", language, 
                                 default="✅ Чудово! Рекомендацію позначено як виконану.\n\nЯк ви себе почуваєте після виконання?")
        
        # Create feedback keyboard
        feedback_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="😊 " + get_text("feel_better", language, default="Краще"),
                    callback_data="feedback_better"
                ),
                InlineKeyboardButton(
                    text="😐 " + get_text("feel_same", language, default="Так само"),
                    callback_data="feedback_same"
                )
            ],
            [
                InlineKeyboardButton(
                    text="😔 " + get_text("feel_worse", language, default="Гірше"),
                    callback_data="feedback_worse"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("skip_feedback", language, default="Пропустити"),
                    callback_data="recommendations"
                )
            ]
        ])
        
        await callback.message.edit_text(
            completion_text,
            reply_markup=feedback_keyboard
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("completion_error", language, default="Помилка збереження"),
            reply_markup=get_recommendations_keyboard(language)
        )

@router.callback_query(F.data.startswith("feedback_"))
async def process_recommendation_feedback(callback: CallbackQuery, language: str = "uk"):
    """Process recommendation feedback"""
    await callback.answer()
    
    feedback_type = callback.data.split("_")[1]  # better, same, worse
    
    feedback_messages = {
        "better": get_text("feedback_better_response", language, 
                          default="🎉 Чудово! Продовжуйте виконувати корисні вправи."),
        "same": get_text("feedback_same_response", language,
                        default="👍 Нормально. Спробуйте інші типи рекомендацій."),
        "worse": get_text("feedback_worse_response", language,
                         default="😔 Вибачте. Можливо, варто звернутися до спеціаліста.")
    }
    
    response_text = feedback_messages.get(feedback_type, "Дякуємо за відгук!")
    
    if feedback_type == "worse":
        response_text += f"\n\n📞 {get_text('crisis_support', language, default='Підтримка')}: 7333"
    
    await callback.message.edit_text(
        response_text,
        reply_markup=get_recommendations_keyboard(language)
    )