from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from utils.texts import get_text

def get_main_menu_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    """Generate main menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🧠 " + get_text("my_mood", language, default="Мій настрій"),
                callback_data="my_mood"
            )
        ],
        [
            InlineKeyboardButton(
                text="💪 " + get_text("recommendations", language, default="Рекомендації"),
                callback_data="recommendations"
            )
        ],
        [
            InlineKeyboardButton(
                text="🤖 " + get_text("ai_chat", language, default="ШІ-чат"),
                callback_data="ai_chat"
            ),
            InlineKeyboardButton(
                text="🎙️ " + get_text("voice_assistant", language, default="Голосовий помічник"),
                callback_data="voice_assistant"
            )
        ],
        [
            InlineKeyboardButton(
                text="📈 " + get_text("mood_stats", language, default="Статистика настрою"),
                callback_data="mood_stats"
            )
        ],
        [
            InlineKeyboardButton(
                text="🧑‍⚕️ " + get_text("psychologist_online", language, default="Психолог онлайн"),
                callback_data="psychologist_online"
            )
        ],
        [
            InlineKeyboardButton(
                text="📜 " + get_text("my_rights", language, default="Мої права"),
                callback_data="my_rights"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏥 " + get_text("telemedicine", language, default="Телемедицина"),
                callback_data="telemedicine"
            )
        ],
        [
            InlineKeyboardButton(
                text="💎 " + get_text("premium", language, default="Преміум"),
                callback_data="premium"
            ),
            InlineKeyboardButton(
                text="📞 " + get_text("hotlines", language, default="Гарячі лінії"),
                callback_data="hotlines"
            )
        ]
    ])
    return keyboard

def get_mood_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    """Generate mood selection keyboard"""
    # Create mood buttons in rows of 5
    buttons = []
    
    # Row 1: 1-5
    row1 = []
    for i in range(1, 6):
        emoji = "😞" if i <= 2 else "😐" if i <= 3 else "🙂"
        row1.append(InlineKeyboardButton(text=f"{i} {emoji}", callback_data=f"mood_{i}"))
    buttons.append(row1)
    
    # Row 2: 6-10  
    row2 = []
    for i in range(6, 11):
        emoji = "🙂" if i <= 7 else "😊" if i <= 8 else "😄"
        row2.append(InlineKeyboardButton(text=f"{i} {emoji}", callback_data=f"mood_{i}"))
    buttons.append(row2)
    
    # Cancel button
    buttons.append([
        InlineKeyboardButton(
            text=get_text("cancel", language),
            callback_data="cancel_mood"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_recommendations_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    """Generate recommendations category keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🫁 " + get_text("breathing_exercises", language, default="Дихальні вправи"),
                callback_data="rec_breathing"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏃‍♂️ " + get_text("physical_exercises", language, default="Фізичні вправи"),
                callback_data="rec_physical"
            )
        ],
        [
            InlineKeyboardButton(
                text="🧘‍♂️ " + get_text("meditation", language, default="Медитації"),
                callback_data="rec_meditation"
            )
        ],
        [
            InlineKeyboardButton(
                text="📚 " + get_text("reading_materials", language, default="Матеріали для читання"),
                callback_data="rec_reading"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎵 " + get_text("relaxing_music", language, default="Розслаблююча музика"),
                callback_data="rec_music"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_menu", language),
                callback_data="main_menu"
            )
        ]
    ])
    return keyboard

def get_ai_chat_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    """Generate AI chat options keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💭 " + get_text("new_chat", language, default="Новий чат"),
                callback_data="new_ai_chat"
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 " + get_text("mood_analysis", language, default="Аналіз настрою"),
                callback_data="ai_mood_analysis"
            )
        ],
        [
            InlineKeyboardButton(
                text="💡 " + get_text("get_advice", language, default="Отримати пораду"),
                callback_data="ai_advice"
            )
        ],
        [
            InlineKeyboardButton(
                text="🧘‍♂️ " + get_text("coping_strategies", language, default="Стратегії подолання"),
                callback_data="ai_coping"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_menu", language),
                callback_data="main_menu"
            )
        ]
    ])
    return keyboard

def get_stats_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    """Generate statistics options keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 " + get_text("weekly_stats", language, default="Тижнева статистика"),
                callback_data="stats_week"
            )
        ],
        [
            InlineKeyboardButton(
                text="📈 " + get_text("monthly_stats", language, default="Місячна статистика"),
                callback_data="stats_month"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔄 " + get_text("mood_trends", language, default="Тренди настрою"),
                callback_data="stats_trends"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 " + get_text("detailed_report", language, default="Детальний звіт"),
                callback_data="stats_detailed"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_menu", language),
                callback_data="main_menu"
            )
        ]
    ])
    return keyboard

def get_legal_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    """Generate legal categories keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎖️ " + get_text("veterans_benefits", language),
                callback_data="legal_benefits"
            )
        ],
        [
            InlineKeyboardButton(
                text="💰 " + get_text("compensation", language),
                callback_data="legal_compensation"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏥 " + get_text("medical_care", language),
                callback_data="legal_medical"
            )
        ],
        [
            InlineKeyboardButton(
                text="⚖️ " + get_text("legal_procedures", language),
                callback_data="legal_procedures"
            )
        ],
        [
            InlineKeyboardButton(
                text="📄 " + get_text("document_templates", language, default="Шаблони документів"),
                callback_data="legal_templates"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_menu", language),
                callback_data="main_menu"
            )
        ]
    ])
    return keyboard

def get_telemedicine_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    """Generate telemedicine options keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📅 " + get_text("book_appointment", language),
                callback_data="book_appointment"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 " + get_text("my_appointments", language),
                callback_data="my_appointments"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔍 " + get_text("find_specialist", language, default="Знайти спеціаліста"),
                callback_data="find_specialist"
            )
        ],
        [
            InlineKeyboardButton(
                text="💊 " + get_text("prescriptions", language, default="Рецепти"),
                callback_data="prescriptions"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_menu", language),
                callback_data="main_menu"
            )
        ]
    ])
    return keyboard

def get_hotlines_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    """Generate hotlines keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🆘 " + get_text("crisis_hotline", language),
                callback_data="hotline_crisis"
            )
        ],
        [
            InlineKeyboardButton(
                text="🧠 " + get_text("mental_health_hotline", language, default="Ментальне здоров'я"),
                callback_data="hotline_mental"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎖️ " + get_text("veterans_hotline", language, default="Лінія ветеранів"),
                callback_data="hotline_veterans"
            )
        ],
        [
            InlineKeyboardButton(
                text="⚖️ " + get_text("legal_hotline", language, default="Правова підтримка"),
                callback_data="hotline_legal"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏥 " + get_text("medical_hotline", language, default="Медична допомога"),
                callback_data="hotline_medical"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_menu", language),
                callback_data="main_menu"
            )
        ]
    ])
    return keyboard

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Generate language selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk"),
            InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")
        ]
    ])
    return keyboard

def get_voice_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    """Generate voice assistant keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎤 " + get_text("record_voice", language, default="Записати голос"),
                callback_data="record_voice"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔊 " + get_text("voice_to_text", language, default="Голос в текст"),
                callback_data="voice_to_text"
            )
        ],
        [
            InlineKeyboardButton(
                text="📢 " + get_text("text_to_speech", language, default="Текст у мову"),
                callback_data="text_to_speech"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_menu", language),
                callback_data="main_menu"
            )
        ]
    ])
    return keyboard