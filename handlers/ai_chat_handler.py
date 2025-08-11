from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db_manager import db_manager
from database.models import AIChat
from services.ai_service import AIService
from utils.keyboards import get_ai_chat_keyboard, get_main_menu_keyboard
from utils.texts import get_text

router = Router()

class AIChatStates(StatesGroup):
    waiting_for_message = State()

@router.callback_query(F.data == "ai_chat")
async def ai_chat_menu(callback: CallbackQuery, language: str = "uk"):
    """Show AI chat menu"""
    await callback.answer()
    
    await callback.message.edit_text(
        get_text("ai_chat_welcome", language),
        reply_markup=get_ai_chat_keyboard(language)
    )

@router.callback_query(F.data == "new_ai_chat")
async def start_new_chat(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Start new AI chat session"""
    await callback.answer()
    
    await callback.message.edit_text(
        get_text("ai_chat_welcome", language) + "\n\n" + get_text("type_your_message", language),
        reply_markup=None
    )
    
    await state.set_state(AIChatStates.waiting_for_message)

@router.message(AIChatStates.waiting_for_message)
async def process_ai_chat_message(message: Message, state: FSMContext, language: str = "uk"):
    """Process AI chat message"""
    user_id = message.from_user.id
    user_message = message.text
    
    # Send processing message
    processing_msg = await message.answer(get_text("ai_processing", language))
    
    try:
        # Get user context
        user = await db_manager.get_user(user_id)
        user_context = {
            "is_veteran": user.is_veteran if user else False,
            "language": language
        }
        
        # Get recent mood if available
        recent_moods = await db_manager.get_user_mood_history(user_id, 1)
        if recent_moods:
            user_context["current_mood"] = recent_moods[0]["mood_level"]
        
        # Get AI response
        ai_service = AIService()
        ai_result = await ai_service.chat_with_ai(
            message=user_message,
            user_context=user_context,
            language=language
        )
        
        ai_response = ai_result["response"]
        
        # Check for crisis indicators
        crisis_check = await ai_service.detect_crisis_indicators(user_message)
        
        # Save chat to database
        chat = AIChat(
            user_id=user_id,
            message=user_message,
            response=ai_response,
            model_used=ai_result.get("model_used", "gemini"),
            is_voice=False
        )
        chat.crisis_flag = crisis_check.get("crisis_detected", False)
        
        await db_manager.save_ai_chat(chat)
        
        # Delete processing message
        await processing_msg.delete()
        
        # Send AI response
        response_text = ai_response
        
        # Add crisis support if needed
        if crisis_check.get("crisis_detected"):
            response_text += f"\n\n🆘 {get_text('crisis_support_notice', language)}"
            response_text += f"\n📞 {get_text('crisis_hotline', language)}: 7333"
        
        await message.answer(
            response_text,
            reply_markup=get_ai_chat_keyboard(language)
        )
        
        await state.clear()
        
    except Exception as e:
        await processing_msg.delete()
        await message.answer(
            get_text("ai_error", language),
            reply_markup=get_main_menu_keyboard(language)
        )
        await state.clear()

@router.callback_query(F.data == "ai_mood_analysis")
async def ai_mood_analysis(callback: CallbackQuery, language: str = "uk"):
    """Provide AI-powered mood analysis"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Get recent mood data
    recent_moods = await db_manager.get_user_mood_history(user_id, 7)
    
    if not recent_moods:
        await callback.message.edit_text(
            get_text("no_mood_data_for_analysis", language),
            reply_markup=get_main_menu_keyboard(language)
        )
        return
    
    processing_msg = await callback.message.edit_text(get_text("ai_processing", language))
    
    try:
        # Prepare mood data for analysis
        mood_summary = []
        for mood in recent_moods[-7:]:  # Last 7 days
            date_str = mood["timestamp"].strftime("%d.%m")
            note = mood.get("note", "")
            mood_summary.append(f"{date_str}: {mood['mood_level']}/10" + (f" - {note}" if note else ""))
        
        mood_text = "\n".join(mood_summary)
        
        analysis_prompt = get_text("mood_analysis_prompt", language).format(mood_data=mood_text)
        
        # Get AI analysis
        ai_service = AIService()
        ai_result = await ai_service.chat_with_ai(
            message=analysis_prompt,
            user_context={"mood_analysis": True},
            language=language
        )
        
        analysis_text = f"📊 {get_text('mood_analysis_title', language)}\n\n"
        analysis_text += ai_result["response"]
        
        await callback.message.edit_text(
            analysis_text,
            reply_markup=get_ai_chat_keyboard(language)
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("ai_error", language),
            reply_markup=get_main_menu_keyboard(language)
        )

@router.callback_query(F.data == "ai_advice")
async def ai_advice(callback: CallbackQuery, language: str = "uk"):
    """Get general AI advice"""
    await callback.answer()
    
    processing_msg = await callback.message.edit_text(get_text("ai_processing", language))
    
    try:
        user_id = callback.from_user.id
        user = await db_manager.get_user(user_id)
        
        # Prepare context-aware advice request
        advice_prompt = get_text("general_advice_prompt", language)
        
        user_context = {
            "is_veteran": user.is_veteran if user else False,
            "advice_request": True
        }
        
        # Get recent mood for context
        recent_moods = await db_manager.get_user_mood_history(user_id, 3)
        if recent_moods:
            avg_mood = sum(m["mood_level"] for m in recent_moods) / len(recent_moods)
            user_context["recent_mood"] = avg_mood
        
        ai_service = AIService()
        ai_result = await ai_service.chat_with_ai(
            message=advice_prompt,
            user_context=user_context,
            language=language
        )
        
        advice_text = f"💡 {get_text('ai_advice_title', language)}\n\n"
        advice_text += ai_result["response"]
        
        await callback.message.edit_text(
            advice_text,
            reply_markup=get_ai_chat_keyboard(language)
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("ai_error", language),
            reply_markup=get_main_menu_keyboard(language)
        )

@router.callback_query(F.data == "ai_coping")
async def ai_coping_strategies(callback: CallbackQuery, language: str = "uk"):
    """Get AI-powered coping strategies"""
    await callback.answer()
    
    processing_msg = await callback.message.edit_text(get_text("ai_processing", language))
    
    try:
        user_id = callback.from_user.id
        user = await db_manager.get_user(user_id)
        
        # Get recent mood for targeted strategies
        recent_moods = await db_manager.get_user_mood_history(user_id, 1)
        current_mood = recent_moods[0]["mood_level"] if recent_moods else 5
        
        coping_prompt = get_text("coping_strategies_prompt", language).format(mood_level=current_mood)
        
        user_context = {
            "is_veteran": user.is_veteran if user else False,
            "current_mood": current_mood,
            "coping_request": True
        }
        
        ai_service = AIService()
        ai_result = await ai_service.chat_with_ai(
            message=coping_prompt,
            user_context=user_context,
            language=language
        )
        
        coping_text = f"🧘‍♂️ {get_text('coping_strategies_title', language)}\n\n"
        coping_text += ai_result["response"]
        
        await callback.message.edit_text(
            coping_text,
            reply_markup=get_ai_chat_keyboard(language)
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("ai_error", language),
            reply_markup=get_main_menu_keyboard(language)
        )