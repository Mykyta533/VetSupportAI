import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
import google.generativeai as genai
import openai
from datetime import datetime

from config import config

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.setup_models()
        
    def setup_models(self):
        """Initialize AI models"""
        # Gemini setup
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
            
        # OpenAI setup
        if config.OPENAI_API_KEY:
            self.openai_client = openai.AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        else:
            self.openai_client = None
    
    async def chat_with_ai(self, message: str, user_context: Dict = None, 
                          language: str = "uk", model: str = "gemini") -> Dict[str, Any]:
        """
        Chat with AI assistant
        """
        try:
            # Prepare system prompt
            system_prompt = self._get_system_prompt(language, user_context)
            
            if model == "gemini" and self.gemini_model:
                response = await self._chat_with_gemini(message, system_prompt)
            elif model == "openai" and self.openai_client:
                response = await self._chat_with_openai(message, system_prompt)
            else:
                # Fallback to a simple response
                response = await self._get_fallback_response(message, language)
            
            return {
                "response": response,
                "model_used": model,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            return {
                "response": self._get_error_response(language),
                "model_used": model,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    async def _chat_with_gemini(self, message: str, system_prompt: str) -> str:
        """Chat with Gemini model"""
        full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
        
        response = await asyncio.to_thread(
            self.gemini_model.generate_content,
            full_prompt
        )
        
        return response.text.strip()
    
    async def _chat_with_openai(self, message: str, system_prompt: str) -> str:
        """Chat with OpenAI model"""
        response = await self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _get_system_prompt(self, language: str, user_context: Dict = None) -> str:
        """Generate system prompt for AI assistant"""
        
        base_prompts = {
            "uk": """
Ви - досвідчений психолог та консультант з ментального здоров'я, який спеціалізується на допомозі ветеранам та людям з травмами.

ВАЖЛИВО: Ви НЕ ставите діагнози та НЕ замінюєте професійну медичну допомогу. Ваша роль - надати підтримку, поради та направити до спеціалістів при необхідності.

Ваші принципи:
- Емпатія та розуміння
- Безоціночне ставлення  
- Фокус на ресурсах людини
- Практичні поради та техніки
- Заохочення до звернення по професійну допомогу при серйозних проблемах

При низькому настрої (1-4) - особлива увага до безпеки та кризової підтримки.
При середньому настрої (5-7) - фокус на стабілізації та покращенні.
При хорошому настрої (8-10) - підтримка позитивного стану та профілактика.

Відповідайте українською мовою, коротко та по суті.
            """,
            
            "en": """
You are an experienced psychologist and mental health counselor specializing in helping veterans and trauma survivors.

IMPORTANT: You do NOT provide diagnoses and do NOT replace professional medical care. Your role is to provide support, advice, and refer to specialists when necessary.

Your principles:
- Empathy and understanding
- Non-judgmental attitude
- Focus on human resources
- Practical advice and techniques
- Encouragement to seek professional help for serious problems

For low mood (1-4) - special attention to safety and crisis support.
For medium mood (5-7) - focus on stabilization and improvement.
For good mood (8-10) - support positive state and prevention.

Respond in English, briefly and to the point.
            """
        }
        
        prompt = base_prompts.get(language, base_prompts["uk"])
        
        if user_context:
            mood = user_context.get("current_mood")
            is_veteran = user_context.get("is_veteran", False)
            recent_mood_trend = user_context.get("mood_trend", "stable")
            
            context_addition = ""
            if mood:
                context_addition += f"\nПоточний настрій користувача: {mood}/10"
            if is_veteran:
                context_addition += f"\nКористувач - ветеран, потребує особливої уваги до ПТСР та військових травм."
            if recent_mood_trend != "stable":
                context_addition += f"\nТренд настрою: {recent_mood_trend}"
                
            prompt += context_addition
        
        return prompt
    
    async def analyze_mood_note(self, note: str, mood_level: int, language: str = "uk") -> Dict[str, Any]:
        """
        Analyze mood note using AI
        """
        try:
            prompt = self._get_mood_analysis_prompt(note, mood_level, language)
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content,
                    prompt
                )
                analysis_text = response.text.strip()
            elif self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.5
                )
                analysis_text = response.choices[0].message.content.strip()
            else:
                return self._get_fallback_mood_analysis(note, mood_level, language)
            
            # Try to parse as JSON, fallback to text
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                analysis = {
                    "summary": analysis_text,
                    "emotions": [],
                    "triggers": [],
                    "suggestions": []
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in mood analysis: {e}")
            return self._get_fallback_mood_analysis(note, mood_level, language)
    
    def _get_mood_analysis_prompt(self, note: str, mood_level: int, language: str) -> str:
        """Generate prompt for mood analysis"""
        if language == "uk":
            return f"""
Проаналізуйте наступний запис про настрій (рівень {mood_level}/10):
"{note}"

Надайте короткий аналіз у форматі JSON з такими полями:
- summary: короткий підсумок (1-2 речення)
- emotions: основні емоції (список)  
- triggers: можливі тригери (список)
- suggestions: 2-3 поради для покращення стану

Відповідь має бути емпатичною та підтримувальною.
            """
        else:
            return f"""
Analyze the following mood entry (level {mood_level}/10):
"{note}"

Provide a brief analysis in JSON format with these fields:
- summary: brief summary (1-2 sentences)
- emotions: main emotions (list)
- triggers: possible triggers (list)  
- suggestions: 2-3 suggestions for improvement

Response should be empathetic and supportive.
            """
    
    async def get_mood_recommendations(self, mood_level: int, note: str = None, 
                                     language: str = "uk") -> List[str]:
        """
        Get personalized recommendations based on mood
        """
        try:
            prompt = self._get_recommendations_prompt(mood_level, note, language)
            
            if self.gemini_model:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content,
                    prompt
                )
                recommendations_text = response.text.strip()
            elif self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400,
                    temperature=0.7
                )
                recommendations_text = response.choices[0].message.content.strip()
            else:
                return self._get_fallback_recommendations(mood_level, language)
            
            # Extract recommendations from response
            recommendations = []
            for line in recommendations_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or 
                           line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                    # Clean up the line
                    clean_line = line.lstrip('-•123456789. ').strip()
                    if clean_line:
                        recommendations.append(clean_line)
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return self._get_fallback_recommendations(mood_level, language)
    
    def _get_recommendations_prompt(self, mood_level: int, note: str, language: str) -> str:
        """Generate prompt for mood recommendations"""
        note_part = f'\nКоментар користувача: "{note}"' if note else ""
        
        if language == "uk":
            return f"""
Користувач має настрій {mood_level}/10.{note_part}

Надайте 3-5 конкретних, практичних рекомендацій для покращення стану:
- Кожна рекомендація має бути короткою (1-2 речення)
- Фокус на дії, які можна виконати зараз
- Врахуйте рівень настрою (низький потребує простих дій, високий - підтримки стану)
- Включіть різні типи активностей (дихальні вправи, рух, ментальні техніки)

Формат: список з дефісами або нумерацією.
            """
        else:
            return f"""
User has mood level {mood_level}/10.{note_part if note else ""}

Provide 3-5 specific, practical recommendations to improve their state:
- Each recommendation should be brief (1-2 sentences)
- Focus on actions that can be done now
- Consider mood level (low needs simple actions, high needs state maintenance)
- Include different types of activities (breathing, movement, mental techniques)

Format: list with dashes or numbering.
            """
    
    def _get_fallback_mood_analysis(self, note: str, mood_level: int, language: str) -> Dict[str, Any]:
        """Fallback mood analysis when AI is unavailable"""
        if language == "uk":
            if mood_level <= 3:
                summary = "Помічаю, що ваш настрій зараз знижений. Це може бути складний період, але пам'ятайте - ви не самі."
                suggestions = [
                    "Спробуйте глибоко подихати кілька разів",
                    "Зверніться до друга або близької людини",
                    "Розгляньте можливість звернення до спеціаліста"
                ]
            elif mood_level <= 6:
                summary = "Ваш настрій у середньому діапазоні. Є простір для покращення стану."
                suggestions = [
                    "Прогулянка на свіжому повітрі може допомогти",
                    "Послухайте улюблену музику",
                    "Зробіть щось приємне для себе"
                ]
            else:
                summary = "Радий, що ваш настрій гарний! Важливо підтримувати такий стан."
                suggestions = [
                    "Поділіться позитивом з іншими",
                    "Запишіть, що принесло вам радість сьогодні",
                    "Плануйте щось приємне на майбутнє"
                ]
        else:
            if mood_level <= 3:
                summary = "I notice your mood is currently low. This might be a difficult period, but remember - you're not alone."
                suggestions = [
                    "Try taking a few deep breaths",
                    "Reach out to a friend or loved one",
                    "Consider seeking professional support"
                ]
            elif mood_level <= 6:
                summary = "Your mood is in the middle range. There's room for improvement."
                suggestions = [
                    "A walk outside might help",
                    "Listen to your favorite music",
                    "Do something nice for yourself"
                ]
            else:
                summary = "Great to see your mood is good! It's important to maintain this state."
                suggestions = [
                    "Share positivity with others",
                    "Write down what brought you joy today",
                    "Plan something pleasant for the future"
                ]
        
        return {
            "summary": summary,
            "emotions": [],
            "triggers": [],
            "suggestions": suggestions
        }
    
    def _get_fallback_recommendations(self, mood_level: int, language: str) -> List[str]:
        """Fallback recommendations when AI is unavailable"""
        if language == "uk":
            if mood_level <= 3:
                return [
                    "Спробуйте дихальну вправу 4-7-8",
                    "Зверніться до близької людини за підтримкою",
                    "Прогуляйтесь на свіжому повітрі 10-15 хвилин",
                    "Випийте теплий чай або воду",
                    "Послухайте заспокійливу музику"
                ]
            elif mood_level <= 6:
                return [
                    "Зробіть невелику фізичну розминку",
                    "Послухайте улюблену музику",
                    "Зателефонуйте другу або родині",
                    "Приготуйте щось смачне",
                    "Подивіться мотивуючий фільм або відео"
                ]
            else:
                return [
                    "Поділіться своїм гарним настроєм з іншими",
                    "Запишіть 3 речі, за які вдячні сьогодні",
                    "Зробіть щось креативне",
                    "Сплануйте приємну активність на майбутнє",
                    "Допоможіть комусь іншому"
                ]
        else:
            if mood_level <= 3:
                return [
                    "Try the 4-7-8 breathing exercise",
                    "Reach out to someone close for support",
                    "Take a 10-15 minute walk outside",
                    "Drink warm tea or water",
                    "Listen to calming music"
                ]
            elif mood_level <= 6:
                return [
                    "Do some light physical exercise",
                    "Listen to your favorite music",
                    "Call a friend or family member",
                    "Cook something delicious",
                    "Watch a motivating movie or video"
                ]
            else:
                return [
                    "Share your good mood with others",
                    "Write down 3 things you're grateful for today",
                    "Do something creative",
                    "Plan a pleasant activity for the future",
                    "Help someone else"
                ]
    
    async def _get_fallback_response(self, message: str, language: str) -> str:
        """Fallback response when AI models are unavailable"""
        if language == "uk":
            return """Дякую за ваше повідомлення. На жаль, зараз у мене технічні проблеми з ШІ-моделлю, але я хочу, щоб ви знали - ваші почуття важливі.

Якщо вам потрібна негайна підтримка:
📞 Лінія довіри: 7333
📞 Психологічна підтримка: 116 123

Спробуйте написати пізніше, або скористайтесь іншими функціями бота."""
        else:
            return """Thank you for your message. Unfortunately, I'm having technical issues with the AI model right now, but I want you to know - your feelings matter.

If you need immediate support:
📞 Crisis line: 7333  
📞 Psychological support: 116 123

Please try again later, or use other bot features."""
    
    def _get_error_response(self, language: str) -> str:
        """Error response when AI fails"""
        if language == "uk":
            return "Вибачте, виникла технічна помилка. Спробуйте пізніше або зверніться до розділу 'Гарячі лінії' за допомогою."
        else:
            return "Sorry, a technical error occurred. Please try again later or check the 'Hotlines' section for support."

    async def detect_crisis_indicators(self, text: str) -> Dict[str, Any]:
        """
        Detect crisis indicators in user text
        """
        crisis_keywords = {
            "uk": [
                "самогубство", "покінчити з життям", "не хочу жити", "краще б помер",
                "немає сенсу", "все безнадійно", "нікому не потрібен", "хочу померти"
            ],
            "en": [
                "suicide", "kill myself", "don't want to live", "better off dead",
                "no point", "hopeless", "nobody cares", "want to die"
            ]
        }
        
        text_lower = text.lower()
        crisis_detected = False
        matched_indicators = []
        
        for lang, keywords in crisis_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    crisis_detected = True
                    matched_indicators.append(keyword)
        
        return {
            "crisis_detected": crisis_detected,
            "confidence": len(matched_indicators) / max(len(text.split()), 1),
            "indicators": matched_indicators,
            "requires_immediate_attention": crisis_detected and len(matched_indicators) >= 2
        }