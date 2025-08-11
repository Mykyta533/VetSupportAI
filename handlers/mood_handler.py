from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta

from database.db_manager import db_manager
from database.models import MoodCheckIn
from services.ai_service import AIService
from utils.keyboards import get_mood_keyboard, get_main_menu_keyboard
from utils.texts import get_text

router = Router()

class MoodStates(StatesGroup):
    waiting_for_mood = State()
    waiting_for_note = State()

@router.callback_query(F.data == "my_mood")
async def my_mood_callback(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Handle mood check-in menu"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Check if user already checked in today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    mood_history = await db_manager.get_user_mood_history(user_id, days=1)
    
    today_checkin = None
    if mood_history:
        last_checkin = mood_history[0]
        if last_checkin['timestamp'] >= today_start:
            today_checkin = last_checkin
    
    if today_checkin:
        # User already checked in today
        mood_level = today_checkin['mood_level']
        mood_emoji = "😢" if mood_level <= 3 else "😐" if mood_level <= 6 else "😊"
        
        message_text = get_text("already_checked_in_today", language).format(
            mood=mood_level,
            emoji=mood_emoji
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("update_mood", language),
                    callback_data="update_mood"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("view_mood_stats", language),
                    callback_data="mood_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back_to_menu", language),
                    callback_data="main_menu"
                )
            ]
        ])
        
        await callback.message.edit_text(message_text, reply_markup=keyboard)
    else:
        # New mood check-in
        await start_mood_checkin(callback, state, language)

@router.callback_query(F.data.in_(["update_mood", "new_mood_checkin"]))
async def start_mood_checkin(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Start mood check-in process"""
    await callback.answer()
    
    await callback.message.edit_text(
        get_text("mood_question", language),
        reply_markup=get_mood_keyboard(language)
    )
    
    await state.set_state(MoodStates.waiting_for_mood)

@router.callback_query(MoodStates.waiting_for_mood, F.data.startswith("mood_"))
async def process_mood_selection(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Process mood level selection"""
    await callback.answer()
    
    mood_level = int(callback.data.split("_")[1])
    await state.update_data(mood_level=mood_level)
    
    mood_emoji = "😢" if mood_level <= 3 else "😐" if mood_level <= 6 else "😊"
    
    note_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("skip_note", language),
                callback_data="skip_note"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("cancel", language),
                callback_data="cancel_mood"
            )
        ]
    ])
    
    await callback.message.edit_text(
        get_text("mood_note_request", language).format(
            mood=mood_level,
            emoji=mood_emoji
        ),
        reply_markup=note_keyboard
    )
    
    await state.set_state(MoodStates.waiting_for_note)

@router.callback_query(MoodStates.waiting_for_note, F.data == "skip_note")
async def skip_note(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Skip note and complete mood check-in"""
    await callback.answer()
    
    data = await state.get_data()
    await complete_mood_checkin(callback, data['mood_level'], None, language)
    await state.clear()

@router.message(MoodStates.waiting_for_note)
async def process_mood_note(message: Message, state: FSMContext, language: str = "uk"):
    """Process mood note"""
    data = await state.get_data()
    mood_level = data['mood_level']
    note = message.text
    
    await complete_mood_checkin(message, mood_level, note, language)
    await state.clear()

async def complete_mood_checkin(message_or_callback, mood_level: int, note: str, language: str):
    """Complete mood check-in process"""
    user_id = message_or_callback.from_user.id
    
    # Create mood check-in
    checkin = MoodCheckIn(user_id=user_id, mood_level=mood_level, note=note)
    
    # Get AI analysis if note is provided
    if note:
        ai_service = AIService()
        analysis = await ai_service.analyze_mood_note(note, mood_level, language)
        checkin.ai_analysis = analysis
        
        # Get personalized recommendations
        recommendations = await ai_service.get_mood_recommendations(mood_level, note, language)
        checkin.recommended_actions = recommendations
    
    # Save to database
    success = await db_manager.create_mood_checkin(checkin)
    
    if success:
        response_text = get_text("mood_saved", language).format(mood=mood_level)
        
        if checkin.ai_analysis:
            response_text += f"\n\n📝 {get_text('ai_insights', language)}:\n{checkin.ai_analysis.get('summary', '')}"
        
        if checkin.recommended_actions:
            response_text += f"\n\n💡 {get_text('recommendations', language)}:\n"
            for i, action in enumerate(checkin.recommended_actions[:3], 1):
                response_text += f"{i}. {action}\n"
        
        # Check if user needs extra support
        if mood_level <= 3:
            response_text += f"\n\n❤️ {get_text('low_mood_support', language)}"
            
            support_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_text("talk_to_ai", language),
                        callback_data="ai_chat"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("breathing_exercise", language),
                        callback_data="breathing_exercise"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("emergency_contacts", language),
                        callback_data="emergency_help"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("back_to_menu", language),
                        callback_data="main_menu"
                    )
                ]
            ])
        else:
            support_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_text("view_recommendations", language),
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
    else:
        response_text = get_text("mood_save_error", language)
        support_keyboard = get_main_menu_keyboard(language)
    
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(response_text, reply_markup=support_keyboard)
    else:
        await message_or_callback.message.edit_text(response_text, reply_markup=support_keyboard)

@router.callback_query(F.data == "breathing_exercise")
async def breathing_exercise_callback(callback: CallbackQuery, language: str = "uk"):
    """Start breathing exercise"""
    await callback.answer()
    
    exercise_text = get_text("breathing_exercise_guide", language)
    
    exercise_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("start_exercise", language),
                callback_data="start_breathing"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_menu", language),
                callback_data="main_menu"
            )
        ]
    ])
    
    await callback.message.edit_text(exercise_text, reply_markup=exercise_keyboard)

@router.callback_query(F.data == "start_breathing")
async def start_breathing_callback(callback: CallbackQuery, language: str = "uk"):
    """Start guided breathing exercise"""
    await callback.answer()
    
    # This would be enhanced with actual breathing guidance
    await callback.message.edit_text(
        get_text("breathing_in_progress", language),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("exercise_complete", language),
                    callback_data="breathing_complete"
                )
            ]
        ])
    )

@router.callback_query(F.data == "breathing_complete")
async def breathing_complete_callback(callback: CallbackQuery, language: str = "uk"):
    """Complete breathing exercise"""
    await callback.answer()
    
    completion_text = get_text("breathing_exercise_complete", language)
    
    await callback.message.edit_text(
        completion_text,
        reply_markup=get_main_menu_keyboard(language)
    )

@router.callback_query(F.data == "emergency_help")
async def emergency_help_callback(callback: CallbackQuery, language: str = "uk"):
    """Show emergency contacts and resources"""
    await callback.answer()
    
    emergency_text = get_text("emergency_resources", language)
    
    emergency_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("crisis_hotline", language),
                callback_data="crisis_hotline"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("find_psychologist", language),
                callback_data="psychologist_online"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_menu", language),
                callback_data="main_menu"
            )
        ]
    ])
    
    await callback.message.edit_text(emergency_text, reply_markup=emergency_keyboard)

@router.callback_query(F.data == "cancel_mood")
async def cancel_mood_callback(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Cancel mood check-in"""
    await callback.answer()
    await state.clear()
    
    await callback.message.edit_text(
        get_text("mood_cancelled", language),
        reply_markup=get_main_menu_keyboard(language)
    )