import asyncio
import os
import logging
from typing import Optional, Dict, Any
import aiohttp
import tempfile
from gtts import gTTS
import io

from config import config

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        self.whisper_url = "https://api.openai.com/v1/audio/transcriptions"
        self.elevenlabs_url = "https://api.elevenlabs.io/v1/text-to-speech"
        
    async def speech_to_text(self, audio_file_path: str, language: str = "uk") -> Dict[str, Any]:
        """
        Convert speech to text using Whisper API
        """
        try:
            if config.OPENAI_API_KEY:
                return await self._whisper_transcribe(audio_file_path, language)
            else:
                return await self._google_speech_to_text(audio_file_path, language)
                
        except Exception as e:
            logger.error(f"Speech to text error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    async def _whisper_transcribe(self, audio_file_path: str, language: str) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper"""
        headers = {
            "Authorization": f"Bearer {config.OPENAI_API_KEY}"
        }
        
        # Map language codes for Whisper
        whisper_lang = "uk" if language == "uk" else "en"
        
        try:
            async with aiohttp.ClientSession() as session:
                with open(audio_file_path, "rb") as audio_file:
                    data = aiohttp.FormData()
                    data.add_field('file', audio_file, filename='audio.ogg')
                    data.add_field('model', 'whisper-1')
                    data.add_field('language', whisper_lang)
                    
                    async with session.post(
                        self.whisper_url,
                        headers=headers,
                        data=data
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return {
                                "success": True,
                                "text": result.get("text", ""),
                                "language": language
                            }
                        else:
                            error_text = await response.text()
                            logger.error(f"Whisper API error: {error_text}")
                            return {
                                "success": False,
                                "error": f"API error: {response.status}",
                                "text": ""
                            }
                            
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    async def _google_speech_to_text(self, audio_file_path: str, language: str) -> Dict[str, Any]:
        """Fallback to Google Speech-to-Text (simplified implementation)"""
        # This would require Google Cloud Speech-to-Text API setup
        # For now, return a placeholder
        return {
            "success": False,
            "error": "Google Speech-to-Text not implemented yet",
            "text": ""
        }
    
    async def text_to_speech(self, text: str, language: str = "uk", 
                           voice: str = "default") -> Dict[str, Any]:
        """
        Convert text to speech
        """
        try:
            if config.ELEVENLABS_API_KEY and voice != "default":
                return await self._elevenlabs_tts(text, voice)
            else:
                return await self._google_tts(text, language)
                
        except Exception as e:
            logger.error(f"Text to speech error: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_file": None
            }
    
    async def _google_tts(self, text: str, language: str) -> Dict[str, Any]:
        """Generate speech using Google TTS"""
        try:
            # Map language codes for gTTS
            gtts_lang = "uk" if language == "uk" else "en"
            
            # Create TTS object
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                tts.save(temp_file.name)
                
                return {
                    "success": True,
                    "audio_file": temp_file.name,
                    "format": "mp3",
                    "language": language
                }
                
        except Exception as e:
            logger.error(f"Google TTS error: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_file": None
            }
    
    async def _elevenlabs_tts(self, text: str, voice_id: str) -> Dict[str, Any]:
        """Generate speech using ElevenLabs API"""
        try:
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": config.ELEVENLABS_API_KEY
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.elevenlabs_url}/{voice_id}",
                    json=data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        audio_content = await response.read()
                        
                        # Create temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                            temp_file.write(audio_content)
                            
                            return {
                                "success": True,
                                "audio_file": temp_file.name,
                                "format": "mp3",
                                "voice": voice_id
                            }
                    else:
                        error_text = await response.text()
                        logger.error(f"ElevenLabs API error: {error_text}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "audio_file": None
                        }
                        
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_file": None
            }
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary audio files"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.error(f"Error cleaning up temp file {file_path}: {e}")

class VoiceAssistant:
    def __init__(self):
        self.voice_service = VoiceService()
        
    async def process_voice_message(self, audio_file_path: str, user_context: Dict = None, 
                                   language: str = "uk") -> Dict[str, Any]:
        """
        Process voice message: speech-to-text -> AI response -> text-to-speech
        """
        try:
            # Step 1: Convert speech to text
            transcription_result = await self.voice_service.speech_to_text(audio_file_path, language)
            
            if not transcription_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to transcribe audio",
                    "transcription": "",
                    "ai_response": "",
                    "audio_response": None
                }
            
            transcribed_text = transcription_result["text"]
            
            # Step 2: Get AI response
            from services.ai_service import AIService
            ai_service = AIService()
            ai_result = await ai_service.chat_with_ai(
                message=transcribed_text,
                user_context=user_context,
                language=language
            )
            
            ai_response_text = ai_result["response"]
            
            # Step 3: Convert AI response to speech
            tts_result = await self.voice_service.text_to_speech(ai_response_text, language)
            
            return {
                "success": True,
                "transcription": transcribed_text,
                "ai_response": ai_response_text,
                "audio_response": tts_result.get("audio_file"),
                "model_used": ai_result.get("model_used", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Voice message processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": "",
                "ai_response": "",
                "audio_response": None
            }
    
    async def generate_mood_audio_response(self, mood_level: int, note: str = None, 
                                         language: str = "uk") -> Optional[str]:
        """
        Generate audio response for mood check-in
        """
        try:
            # Generate appropriate text response based on mood
            if language == "uk":
                if mood_level <= 3:
                    text = f"Дякую, що поділилися своїм настроєм. Помічаю, що зараз вам важко. Пам'ятайте - ви не самі, і я тут, щоб підтримати вас. Можливо, варто спробувати глибоко подихати або звернутися до близької людини."
                elif mood_level <= 6:
                    text = f"Дякую за відкритість. Ваш настрій у середньому діапазоні, є можливості для покращення. Спробуйте зробити щось приємне для себе - прогуляйтесь або послухайте улюблену музику."
                else:
                    text = f"Чудово, що ваш настрій гарний! Це дуже важливо. Намагайтесь зберігати це відчуття та ділитесь позитивом з оточуючими."
            else:
                if mood_level <= 3:
                    text = f"Thank you for sharing your mood with me. I can see you're having a difficult time right now. Remember - you're not alone, and I'm here to support you. Maybe try taking deep breaths or reaching out to someone close."
                elif mood_level <= 6:
                    text = f"Thank you for being open. Your mood is in the middle range, there are opportunities for improvement. Try doing something nice for yourself - take a walk or listen to your favorite music."
                else:
                    text = f"Wonderful that your mood is good! This is very important. Try to maintain this feeling and share positivity with those around you."
            
            # Convert to speech
            tts_result = await self.voice_service.text_to_speech(text, language)
            
            if tts_result["success"]:
                return tts_result["audio_file"]
            else:
                logger.error(f"Failed to generate mood audio response: {tts_result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating mood audio response: {e}")
            return None