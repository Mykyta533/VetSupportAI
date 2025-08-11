from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Voice, Audio, Document
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import tempfile
import os
import logging

from database.db_manager import db_manager
from database.models import AIChat
from services.voice_service import VoiceAssistant, VoiceService
from utils.keyboards import get_voice_keyboard, get_main_menu_keyboard
from utils.texts import get_text

router = Router()
logger = logging.getLogger(__name__)

class VoiceStates(StatesGroup):
    waiting_for_voice = State()
    waiting_for_text = State()

@router.callback_query(F.data == "voice_assistant")
async def voice_assistant_menu(callback: CallbackQuery, language: str = "uk"):
    """Show voice assistant menu"""
    await callback.answer()
    
    menu_text = get_text("voice_assistant_welcome", language)
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=get_voice_keyboard(language)
    )

@router.callback_query(F.data == "record_voice")
async def start_voice_recording(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Start voice message recording"""
    await callback.answer()
    
    instruction_text = get_text("voice_recording_instruction", language)
    
    await callback.message.edit_text(
        instruction_text,
        reply_markup=None
    )
    
    await state.set_state(VoiceStates.waiting_for_voice)

@router.message(VoiceStates.waiting_for_voice, F.voice)
async def process_voice_message(message: Message, state: FSMContext, language: str = "uk"):
    """Process voice message"""
    user_id = message.from_user.id
    
    # Send processing message
    processing_msg = await message.answer(get_text("voice_processing", language))
    
    try:
        # Download voice file
        voice_file = message.voice
        file_info = await message.bot.get_file(voice_file.file_id)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
            await message.bot.download_file(file_info.file_path, temp_file)
            temp_file_path = temp_file.name
        
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
        
        # Process voice message
        voice_assistant = VoiceAssistant()
        result = await voice_assistant.process_voice_message(
            temp_file_path, user_context, language
        )
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Delete processing message
        await processing_msg.delete()
        
        if result["success"]:
            # Send transcription
            transcription_text = f"🎤 {get_text('voice_transcribed', language)}:\n\"{result['transcription']}\""
            await message.answer(transcription_text)
            
            # Send AI response as text
            ai_response_text = f"🤖 {get_text('ai_response', language)}:\n{result['ai_response']}"
            await message.answer(ai_response_text)
            
            # Send AI response as voice if available
            if result["audio_response"]:
                try:
                    with open(result["audio_response"], "rb") as audio_file:
                        await message.answer_voice(audio_file)
                    
                    # Clean up audio file
                    voice_assistant.voice_service.cleanup_temp_file(result["audio_response"])
                except Exception as e:
                    logger.error(f"Error sending voice response: {e}")
            
            # Save chat to database
            chat = AIChat(
                user_id=user_id,
                message=result["transcription"],
                response=result["ai_response"],
                model_used=result.get("model_used", "gemini"),
                is_voice=True
            )
            await db_manager.save_ai_chat(chat)
            
            # Show voice menu again
            await message.answer(
                get_text("voice_session_complete", language),
                reply_markup=get_voice_keyboard(language)
            )
            
        else:
            await message.answer(
                get_text("voice_processing_error", language) + f"\n{result.get('error', '')}",
                reply_markup=get_main_menu_keyboard(language)
            )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        
        # Clean up files
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
        except:
            pass
        
        await processing_msg.delete()
        await message.answer(
            get_text("voice_processing_error", language),
            reply_markup=get_main_menu_keyboard(language)
        )
        await state.clear()

@router.message(VoiceStates.waiting_for_voice)
async def handle_non_voice_in_voice_mode(message: Message, state: FSMContext, language: str = "uk"):
    """Handle non-voice messages when expecting voice"""
    if message.text and message.text.startswith('/'):
        # Allow commands to cancel voice mode
        await state.clear()
        return
    
    await message.answer(
        get_text("voice_expected", language),
        reply_markup=get_voice_keyboard(language)
    )

@router.callback_query(F.data == "voice_to_text")
async def voice_to_text_mode(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Start voice-to-text mode"""
    await callback.answer()
    
    instruction_text = get_text("voice_to_text_instruction", language)
    
    await callback.message.edit_text(
        instruction_text,
        reply_markup=None
    )
    
    await state.set_state(VoiceStates.waiting_for_voice)
    await state.update_data(mode="transcribe_only")

@router.message(VoiceStates.waiting_for_voice, F.voice)
async def transcribe_voice_only(message: Message, state: FSMContext, language: str = "uk"):
    """Transcribe voice message without AI response"""
    # Check if we're in transcribe-only mode
    data = await state.get_data()
    if data.get("mode") != "transcribe_only":
        # Regular voice processing
        await process_voice_message(message, state, language)
        return
    
    processing_msg = await message.answer(get_text("transcribing_voice", language))
    
    try:
        # Download voice file
        voice_file = message.voice
        file_info = await message.bot.get_file(voice_file.file_id)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
            await message.bot.download_file(file_info.file_path, temp_file)
            temp_file_path = temp_file.name
        
        # Transcribe voice
        voice_service = VoiceService()
        result = await voice_service.speech_to_text(temp_file_path, language)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Delete processing message
        await processing_msg.delete()
        
        if result["success"]:
            transcription_text = f"📝 {get_text('transcription_result', language)}:\n\n\"{result['text']}\""
            await message.answer(transcription_text)
        else:
            await message.answer(
                get_text("transcription_error", language) + f"\n{result.get('error', '')}"
            )
        
        # Return to voice menu
        await message.answer(
            get_text("transcription_complete", language),
            reply_markup=get_voice_keyboard(language)
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Voice transcription error: {e}")
        
        # Clean up files
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
        except:
            pass
        
        await processing_msg.delete()
        await message.answer(
            get_text("transcription_error", language),
            reply_markup=get_main_menu_keyboard(language)
        )
        await state.clear()

@router.callback_query(F.data == "text_to_speech")
async def text_to_speech_mode(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Start text-to-speech mode"""
    await callback.answer()
    
    instruction_text = get_text("text_to_speech_instruction", language)
    
    await callback.message.edit_text(
        instruction_text,
        reply_markup=None
    )
    
    await state.set_state(VoiceStates.waiting_for_text)

@router.message(VoiceStates.waiting_for_text)
async def convert_text_to_speech(message: Message, state: FSMContext, language: str = "uk"):
    """Convert text message to speech"""
    if not message.text:
        await message.answer(get_text("text_expected", language))
        return
    
    if message.text.startswith('/'):
        # Allow commands to cancel TTS mode
        await state.clear()
        return
    
    processing_msg = await message.answer(get_text("generating_speech", language))
    
    try:
        # Generate speech
        voice_service = VoiceService()
        result = await voice_service.text_to_speech(message.text, language)
        
        # Delete processing message
        await processing_msg.delete()
        
        if result["success"]:
            # Send audio file
            with open(result["audio_file"], "rb") as audio_file:
                await message.answer_voice(audio_file)
            
            # Clean up audio file
            voice_service.cleanup_temp_file(result["audio_file"])
            
            await message.answer(get_text("speech_generated", language))
        else:
            await message.answer(
                get_text("speech_generation_error", language) + f"\n{result.get('error', '')}"
            )
        
        # Return to voice menu
        await message.answer(
            get_text("tts_complete", language),
            reply_markup=get_voice_keyboard(language)
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Text-to-speech error: {e}")
        
        await processing_msg.delete()
        await message.answer(
            get_text("speech_generation_error", language),
            reply_markup=get_main_menu_keyboard(language)
        )
        await state.clear()

# Handle audio files and documents as voice messages
@router.message(F.audio | F.document.as_("audio_doc"))
async def handle_audio_file(message: Message, state: FSMContext, language: str = "uk"):
    """Handle audio files and documents as voice messages"""
    current_state = await state.get_state()
    
    if current_state != VoiceStates.waiting_for_voice:
        return
    
    processing_msg = await message.answer(get_text("processing_audio_file", language))
    
    try:
        # Determine file type and get file info
        if message.audio:
            file_info = await message.bot.get_file(message.audio.file_id)
            file_extension = ".mp3"
        else:  # document
            audio_doc = message.document
            file_info = await message.bot.get_file(audio_doc.file_id)
            file_extension = os.path.splitext(audio_doc.file_name)[1] or ".mp3"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            await message.bot.download_file(file_info.file_path, temp_file)
            temp_file_path = temp_file.name
        
        # Process as voice message (reuse the voice processing logic)
        # This would require adapting the voice processing to handle different audio formats
        await message.answer(get_text("audio_file_received", language))
        
        # For now, suggest using voice messages instead
        await processing_msg.delete()
        await message.answer(
            get_text("use_voice_message", language),
            reply_markup=get_voice_keyboard(language)
        )
        
        # Clean up
        os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Audio file processing error: {e}")
        
        await processing_msg.delete()
        await message.answer(
            get_text("audio_processing_error", language),
            reply_markup=get_main_menu_keyboard(language)
        )

# Cancel voice operations
@router.callback_query(F.data == "cancel_voice")
async def cancel_voice_operation(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Cancel ongoing voice operation"""
    await callback.answer()
    await state.clear()
    
    await callback.message.edit_text(
        get_text("voice_cancelled", language),
        reply_markup=get_main_menu_keyboard(language)
    )