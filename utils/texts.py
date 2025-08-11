"""
Multilingual text resources for the VetSupport AI Bot
"""

TEXTS = {
    "uk": {
        # Welcome and registration
        "welcome_new_user": """
👋 Вітаємо у VetSupport AI!

Я ваш персональний асистент для підтримки ментального здоров'я. Разом ми будемо:

🧠 Відстежувати ваш настрій щодня
💪 Отримувати персональні рекомендації
🤖 Спілкуватись з ШІ-підтримкою
📈 Аналізувати ваш прогрес
🧑‍⚕️ З'єднуватись з психологами
📜 Отримувати правову допомогу

Для продовження, будь ласка, прийміть наші Умови використання та Політику конфіденційності.
        """,
        
        "welcome_back": "Радий бачити вас знову, {name}! 👋\nЯк справи сьогодні?",
        
        "accept_terms": "✅ Приймаю умови",
        "read_terms": "📖 Читати умови",
        "back_to_registration": "⬅️ Назад до реєстрації",
        
        "veteran_question": "Чи є ви ветераном Збройних Сил України або учасником бойових дій? 🇺🇦",
        "yes_veteran": "✅ Так",
        "no_veteran": "❌ Ні",
        
        "registration_complete": "Реєстрація завершена! 🎉\n\nТепер ви можете користуватись всіма функціями бота.",
        "veteran_benefits": "Як ветеран, ви маєте доступ до спеціальних програм підтримки та пільг. Детальніше в розділі 'Мої права'.",
        "registration_error": "Помилка реєстрації. Спробуйте пізніше.",
        
        # Main menu
        "main_menu": "🏠 Головне меню",
        "back_to_menu": "🔙 Назад до меню",
        
        # Mood tracking
        "mood_question": "Як ваш настрій сьогодні? Оберіть від 1 (дуже погано) до 10 (відмінно):",
        "mood_note_request": "Ваш настрій: {mood}/10 {emoji}\n\nБажаєте додати коментар про те, що вплинуло на ваш настрій?",
        "skip_note": "Пропустити коментар",
        "cancel": "❌ Скасувати",
        "mood_saved": "✅ Настрій збережено: {mood}/10\n\nДякуємо за відкритість!",
        "mood_save_error": "❌ Помилка збереження настрою. Спробуйте пізніше.",
        "mood_cancelled": "Відстеження настрою скасовано.",
        
        "already_checked_in_today": "Сьогодні ви вже відзначили настрій: {mood}/10 {emoji}",
        "update_mood": "🔄 Оновити настрій",
        "view_mood_stats": "📊 Переглянути статистику",
        
        # AI analysis
        "ai_insights": "Аналіз ШІ",
        "recommendations": "Рекомендації",
        "low_mood_support": "Я помітив, що ваш настрій знижений. Пам'ятайте - ви не самі, і це тимчасово. Ось що може допомогти:",
        
        # Exercises and recommendations  
        "breathing_exercise": "🫁 Дихальна вправа",
        "breathing_exercise_guide": """
🫁 Дихальна вправа "4-7-8"

Ця техніка допомагає заспокоїтись та зменшити стрес.

📝 Інструкція:
1. Вдих через ніс на 4 рахунки
2. Затримка дихання на 7 рахунків  
3. Видих через рот на 8 рахунків
4. Повторити 3-4 рази

Готові почати?
        """,
        "start_exercise": "▶️ Почати вправу",
        "breathing_in_progress": "🫁 Слідуйте ритму:\n\n▶️ Вдих (4)... Затримка (7)... Видих (8)...\n\nПовторіть ще кілька разів у своєму темпі.",
        "exercise_complete": "✅ Вправу завершено",
        "breathing_exercise_complete": "🎉 Чудово! Ви завершили дихальну вправу.\n\nЯк ви себе почуваєте зараз?",
        
        # Emergency support
        "emergency_help": "🆘 Екстрена допомога",
        "emergency_resources": """
🆘 Ресурси екстреної допомоги

Якщо ви відчуваєте кризовий стан або потребуєте негайної допомоги:

📞 Національна гаряча лінія з попередження самогубств:
🔸 7333 (безкоштовно)

📞 Лінія психологічної підтримки:
🔸 116 123 (цілодобово)

🏥 Виклик швидкої допомоги:
🔸 103

Пам'ятайте: ви важливі, ваше життя має цінність! 💚
        """,
        "crisis_hotline": "📞 Гаряча лінія",
        "find_psychologist": "👨‍⚕️ Знайти психолога",
        
        # AI Chat
        "talk_to_ai": "🤖 Поговорити з ШІ",
        "ai_chat_welcome": "🤖 Привіт! Я ваш ШІ-асистент для підтримки.\n\nРозкажіть, що вас турбує, або поставте будь-яке питання.",
        "ai_processing": "🤔 Обдумую вашу відповідь...",
        "ai_error": "Вибачте, виникла помилка. Спробуйте пізніше.",
        
        # Statistics and tracking
        "mood_stats": "📈 Статистика настрою",
        "no_mood_data": "📊 Поки що немає даних для відображення.\nПочніть відстежувати свій настрою щодня!",
        
        # Legal section
        "my_rights": "📜 Мої права",
        "legal_categories": "Оберіть категорію:",
        "veterans_benefits": "🎖️ Пільги ветеранів",
        "compensation": "💰 Компенсації",
        "medical_care": "🏥 Медична допомога",
        "legal_procedures": "⚖️ Правові процедури",
        
        # Telemedicine
        "telemedicine": "🏥 Телемедицина",
        "book_appointment": "📅 Записатись на прийом",
        "my_appointments": "📋 Мої записи",
        
        # Premium
        "premium": "💎 Преміум",
        "premium_benefits": """
💎 VetSupport AI Premium

Отримайте безлімітний доступ до:
✨ Необмежених чатів з ШІ
🎯 Персональних рекомендацій
👨‍⚕️ Прямих консультацій з психологами
📊 Детальної аналітики настрою
🔒 Пріоритетної підтримки

Ціна: {price} грн/місяць
        """,
        "subscribe_premium": "💳 Оформити підписку",
        
        # Hotlines
        "hotlines": "📞 Гарячі лінії",
        
        # Common phrases
        "help_text": """
ℹ️ Довідка по боту

Доступні команди:
/start - Почати роботу з ботом
/help - Показати цю довідку  
/menu - Головне меню

Функції бота:
🧠 Щоденне відстеження настрою
💪 Персональні рекомендації
🤖 ШІ-чат для підтримки
📈 Аналітика та статистика
🧑‍⚕️ Зв'язок з психологами
📜 Правова інформація для ветеранів
🏥 Телемедичні послуги

Для навігації використовуйте кнопки меню.
        """,
        
        "terms_and_conditions": """
📋 Умови використання та Політика конфіденційності

VetSupport AI - це інформаційний інструмент для підтримки ментального здоров'я. 

⚠️ ВАЖЛИВЕ ЗАСТЕРЕЖЕННЯ:
Цей бот НЕ замінює професійну медичну допомогу або діагностику. У разі серйозних проблем зі здоров'ям звертайтесь до лікарів.

🔒 Конфіденційність:
• Ваші дані захищені та використовуються тільки для надання послуг
• Ми не передаємо персональну інформацію третім сторонам
• Ви можете видалити свої дані в будь-який час

📞 При кризових ситуаціях негайно звертайтесь за професійною допомогою:
- Телефон довіри: 7333
- Швидка допомога: 103

Користуючись ботом, ви погоджуєтесь з цими умовами.
        """
    },
    
    "en": {
        # Welcome and registration
        "welcome_new_user": """
👋 Welcome to VetSupport AI!

I'm your personal mental health support assistant. Together we will:

🧠 Track your mood daily
💪 Get personalized recommendations
🤖 Chat with AI support
📈 Analyze your progress
🧑‍⚕️ Connect with psychologists
📜 Get legal assistance

To continue, please accept our Terms of Service and Privacy Policy.
        """,
        
        "welcome_back": "Great to see you again, {name}! 👋\nHow are you feeling today?",
        
        "accept_terms": "✅ Accept terms",
        "read_terms": "📖 Read terms",
        "back_to_registration": "⬅️ Back to registration",
        
        "veteran_question": "Are you a veteran of the Armed Forces of Ukraine or a participant in combat operations? 🇺🇦",
        "yes_veteran": "✅ Yes",
        "no_veteran": "❌ No",
        
        "registration_complete": "Registration completed! 🎉\n\nYou can now use all bot features.",
        "veteran_benefits": "As a veteran, you have access to special support programs and benefits. More details in the 'My Rights' section.",
        "registration_error": "Registration error. Please try again later.",
        
        # Main menu
        "main_menu": "🏠 Main Menu",
        "back_to_menu": "🔙 Back to menu",
        
        # Mood tracking
        "mood_question": "How is your mood today? Choose from 1 (very bad) to 10 (excellent):",
        "mood_note_request": "Your mood: {mood}/10 {emoji}\n\nWould you like to add a comment about what affected your mood?",
        "skip_note": "Skip comment",
        "cancel": "❌ Cancel",
        "mood_saved": "✅ Mood saved: {mood}/10\n\nThank you for being open!",
        "mood_save_error": "❌ Error saving mood. Please try again later.",
        "mood_cancelled": "Mood tracking cancelled.",
        
        "already_checked_in_today": "You've already checked your mood today: {mood}/10 {emoji}",
        "update_mood": "🔄 Update mood",
        "view_mood_stats": "📊 View statistics",
        
        # AI analysis
        "ai_insights": "AI Analysis",
        "recommendations": "Recommendations",
        "low_mood_support": "I noticed your mood is low. Remember - you're not alone, and this is temporary. Here's what might help:",
        
        # Exercises and recommendations
        "breathing_exercise": "🫁 Breathing Exercise",
        "breathing_exercise_guide": """
🫁 "4-7-8" Breathing Exercise

This technique helps calm down and reduce stress.

📝 Instructions:
1. Inhale through nose for 4 counts
2. Hold breath for 7 counts
3. Exhale through mouth for 8 counts
4. Repeat 3-4 times

Ready to start?
        """,
        "start_exercise": "▶️ Start exercise",
        "breathing_in_progress": "🫁 Follow the rhythm:\n\n▶️ Inhale (4)... Hold (7)... Exhale (8)...\n\nRepeat a few more times at your own pace.",
        "exercise_complete": "✅ Exercise completed",
        "breathing_exercise_complete": "🎉 Great! You've completed the breathing exercise.\n\nHow do you feel now?",
        
        # Emergency support
        "emergency_help": "🆘 Emergency Help",
        "emergency_resources": """
🆘 Emergency Support Resources

If you're experiencing a crisis or need immediate help:

📞 National Suicide Prevention Hotline:
🔸 7333 (free)

📞 Psychological Support Line:
🔸 116 123 (24/7)

🏥 Emergency Services:
🔸 103

Remember: you matter, your life has value! 💚
        """,
        "crisis_hotline": "📞 Crisis Hotline",
        "find_psychologist": "👨‍⚕️ Find Psychologist",
        
        # AI Chat
        "talk_to_ai": "🤖 Talk to AI",
        "ai_chat_welcome": "🤖 Hi! I'm your AI support assistant.\n\nTell me what's bothering you, or ask any question.",
        "ai_processing": "🤔 Thinking about your message...",
        "ai_error": "Sorry, an error occurred. Please try again later.",
        
        # Statistics and tracking
        "mood_stats": "📈 Mood Statistics",
        "no_mood_data": "📊 No data to display yet.\nStart tracking your mood daily!",
        
        # Legal section
        "my_rights": "📜 My Rights",
        "legal_categories": "Choose category:",
        "veterans_benefits": "🎖️ Veterans Benefits",
        "compensation": "💰 Compensation",
        "medical_care": "🏥 Medical Care",
        "legal_procedures": "⚖️ Legal Procedures",
        
        # Telemedicine
        "telemedicine": "🏥 Telemedicine",
        "book_appointment": "📅 Book Appointment",
        "my_appointments": "📋 My Appointments",
        
        # Premium
        "premium": "💎 Premium",
        "premium_benefits": """
💎 VetSupport AI Premium

Get unlimited access to:
✨ Unlimited AI chats
🎯 Personalized recommendations
👨‍⚕️ Direct psychologist consultations
📊 Detailed mood analytics
🔒 Priority support

Price: {price} UAH/month
        """,
        "subscribe_premium": "💳 Subscribe",
        
        # Hotlines
        "hotlines": "📞 Hotlines",
        
        # Common phrases
        "help_text": """
ℹ️ Bot Help

Available commands:
/start - Start using the bot
/help - Show this help
/menu - Main menu

Bot features:
🧠 Daily mood tracking
💪 Personalized recommendations
🤖 AI chat support
📈 Analytics and statistics
🧑‍⚕️ Connect with psychologists
📜 Legal information for veterans
🏥 Telemedicine services

Use menu buttons for navigation.
        """,
        
        "terms_and_conditions": """
📋 Terms of Service and Privacy Policy

VetSupport AI is an informational mental health support tool.

⚠️ IMPORTANT DISCLAIMER:
This bot does NOT replace professional medical care or diagnosis. For serious health issues, consult doctors.

🔒 Privacy:
• Your data is protected and used only to provide services
• We don't share personal information with third parties
• You can delete your data at any time

📞 In crisis situations, immediately seek professional help:
- Crisis hotline: 7333
- Emergency services: 103

By using the bot, you agree to these terms.
        """
    }
}

def get_text(key: str, language: str = "uk") -> str:
    """Get localized text by key"""
    return TEXTS.get(language, TEXTS["uk"]).get(key, f"Missing text: {key}")

def format_text(key: str, language: str = "uk", **kwargs) -> str:
    """Get and format localized text"""
    text = get_text(key, language)
    try:
        return text.format(**kwargs)
    except KeyError:
        return text