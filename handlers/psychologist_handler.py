from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.keyboards import get_main_menu_keyboard
from utils.texts import get_text

router = Router()

@router.callback_query(F.data == "psychologist_online")
async def psychologist_menu(callback: CallbackQuery, language: str = "uk"):
    """Show psychologist connection menu"""
    await callback.answer()
    
    menu_text = f"🧑‍⚕️ **{get_text('psychologist_online_title', language, default='Психолог онлайн')}**\n\n"
    menu_text += get_text("psychologist_intro", language,
                         default="Професійна психологічна допомога від кваліфікованих спеціалістів, які розуміють особливості роботи з ветеранами.")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("find_psychologist", language, default="Знайти психолога"),
                callback_data="find_psychologist"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("emergency_consultation", language, default="Екстрена консультація"),
                callback_data="emergency_consultation"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("group_therapy", language, default="Групова терапія"),
                callback_data="group_therapy"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("my_sessions", language, default="Мої сесії"),
                callback_data="my_sessions"
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
        menu_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "find_psychologist")
async def find_psychologist(callback: CallbackQuery, language: str = "uk"):
    """Show psychologist search options"""
    await callback.answer()
    
    search_text = f"🔍 **{get_text('find_psychologist_title', language, default='Пошук психолога')}**\n\n"
    search_text += get_text("psychologist_search_intro", language,
                           default="Оберіть спеціалізацію психолога відповідно до ваших потреб:")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎖️ " + get_text("military_trauma", language, default="Військові травми та ПТСР"),
                callback_data="psych_military"
            )
        ],
        [
            InlineKeyboardButton(
                text="😔 " + get_text("depression_anxiety", language, default="Депресія та тривожність"),
                callback_data="psych_depression"
            )
        ],
        [
            InlineKeyboardButton(
                text="👨‍👩‍👧‍👦 " + get_text("family_therapy", language, default="Сімейна терапія"),
                callback_data="psych_family"
            )
        ],
        [
            InlineKeyboardButton(
                text="🧠 " + get_text("cognitive_therapy", language, default="Когнітивно-поведінкова терапія"),
                callback_data="psych_cognitive"
            )
        ],
        [
            InlineKeyboardButton(
                text="💊 " + get_text("addiction_help", language, default="Допомога з залежностями"),
                callback_data="psych_addiction"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_psychologist", language, default="Назад до психологів"),
                callback_data="psychologist_online"
            )
        ]
    ])
    
    await callback.message.edit_text(
        search_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("psych_"))
async def show_psychologist_category(callback: CallbackQuery, language: str = "uk"):
    """Show psychologists in specific category"""
    await callback.answer()
    
    category = callback.data.split("_")[1]
    
    category_info = {
        "military": {
            "title": get_text("military_trauma_specialists", language, default="Спеціалісти з військових травм"),
            "description": get_text("military_trauma_desc", language,
                                  default="Психологи, які спеціалізуються на роботі з ветеранами та військовими травмами. Мають досвід роботи з ПТСР, флешбеками, проблемами адаптації."),
            "specialists": [
                {"name": "Др. Олена Петренко", "experience": "15 років", "rating": "4.9"},
                {"name": "Др. Андрій Коваленко", "experience": "12 років", "rating": "4.8"},
                {"name": "Др. Марія Іваненко", "experience": "10 років", "rating": "4.9"}
            ]
        },
        "depression": {
            "title": get_text("depression_specialists", language, default="Спеціалісти з депресії"),
            "description": get_text("depression_desc", language,
                                  default="Психологи, які працюють з депресивними розладами, тривожністю та емоційними проблемами."),
            "specialists": [
                {"name": "Др. Світлана Мельник", "experience": "18 років", "rating": "4.9"},
                {"name": "Др. Ігор Савченко", "experience": "14 років", "rating": "4.7"},
                {"name": "Др. Наталія Бондар", "experience": "11 років", "rating": "4.8"}
            ]
        },
        "family": {
            "title": get_text("family_therapists", language, default="Сімейні терапевти"),
            "description": get_text("family_therapy_desc", language,
                                  default="Спеціалісти з сімейної терапії, які допомагають відновити стосунки та вирішити сімейні конфлікти."),
            "specialists": [
                {"name": "Др. Тетяна Лисенко", "experience": "16 років", "rating": "4.8"},
                {"name": "Др. Василь Кравченко", "experience": "13 років", "rating": "4.7"}
            ]
        },
        "cognitive": {
            "title": get_text("cognitive_therapists", language, default="КПТ терапевти"),
            "description": get_text("cognitive_therapy_desc", language,
                                  default="Спеціалісти з когнітивно-поведінкової терапії, ефективної при тривожності, депресії та ПТСР."),
            "specialists": [
                {"name": "Др. Олександр Морозов", "experience": "14 років", "rating": "4.9"},
                {"name": "Др. Юлія Шевченко", "experience": "12 років", "rating": "4.8"}
            ]
        },
        "addiction": {
            "title": get_text("addiction_specialists", language, default="Спеціалісти з залежностей"),
            "description": get_text("addiction_desc", language,
                                  default="Психологи, які працюють з різними видами залежностей та допомагають у відновленні."),
            "specialists": [
                {"name": "Др. Роман Гриценко", "experience": "17 років", "rating": "4.8"},
                {"name": "Др. Ірина Полякова", "experience": "13 років", "rating": "4.7"}
            ]
        }
    }
    
    info = category_info.get(category)
    if not info:
        await callback.message.edit_text(
            get_text("category_not_found", language, default="Категорія не знайдена"),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text("back_to_search", language, default="Назад до пошуку"), callback_data="find_psychologist")]
            ])
        )
        return
    
    specialists_text = f"👨‍⚕️ **{info['title']}**\n\n"
    specialists_text += f"📝 {info['description']}\n\n"
    specialists_text += f"**{get_text('available_specialists', language, default='Доступні спеціалісти')}:**\n\n"
    
    keyboard_buttons = []
    
    for i, specialist in enumerate(info['specialists'], 1):
        specialists_text += f"{i}. **{specialist['name']}**\n"
        specialists_text += f"   📅 {get_text('experience', language, default='Досвід')}: {specialist['experience']}\n"
        specialists_text += f"   ⭐ {get_text('rating', language, default='Рейтинг')}: {specialist['rating']}/5.0\n\n"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📅 {get_text('book_session', language, default='Записатися')} - {specialist['name']}",
                callback_data=f"book_session_{i}_{category}"
            )
        ])
    
    keyboard_buttons.extend([
        [
            InlineKeyboardButton(
                text=get_text("back_to_search", language, default="Назад до пошуку"),
                callback_data="find_psychologist"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_psychologist", language, default="Назад до психологів"),
                callback_data="psychologist_online"
            )
        ]
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(
        specialists_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("book_session_"))
async def book_session(callback: CallbackQuery, language: str = "uk"):
    """Book session with psychologist"""
    await callback.answer()
    
    # Parse callback data
    parts = callback.data.split("_")
    specialist_id = parts[2]
    category = parts[3]
    
    booking_text = f"📅 **{get_text('session_booking', language, default='Запис на сесію')}**\n\n"
    booking_text += get_text("booking_process", language,
                           default="Для запису на консультацію з психологом:\n\n1. Оберіть зручний час\n2. Вкажіть тип консультації\n3. Опишіть основну проблему\n4. Підтвердіть запис")
    
    booking_text += f"\n\n⚠️ **{get_text('important_note', language, default='Важлива інформація')}:**\n"
    booking_text += get_text("booking_notice", language,
                           default="Система запису знаходиться в розробці. Наразі ви можете зв'язатися з нашою підтримкою для організації консультації.")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("contact_support_booking", language, default="Зв'язатися з підтримкою"),
                callback_data="psychologist_support"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("emergency_consultation", language, default="Екстрена консультація"),
                callback_data="emergency_consultation"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_specialists", language, default="Назад до спеціалістів"),
                callback_data=f"psych_{category}"
            )
        ]
    ])
    
    await callback.message.edit_text(
        booking_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "emergency_consultation")
async def emergency_consultation(callback: CallbackQuery, language: str = "uk"):
    """Handle emergency consultation request"""
    await callback.answer()
    
    emergency_text = f"🆘 **{get_text('emergency_consultation_title', language, default='Екстрена консультація')}**\n\n"
    emergency_text += get_text("emergency_intro", language,
                             default="Якщо ви перебуваєте в кризовому стані або потребуєте негайної психологічної допомоги:")
    
    emergency_text += f"\n\n📞 **{get_text('immediate_help', language, default='Негайна допомога')}:**\n"
    emergency_text += f"• {get_text('crisis_line', language, default='Кризова лінія')}: 7333\n"
    emergency_text += f"• {get_text('psychological_support', language, default='Психологічна підтримка')}: 116 123\n"
    emergency_text += f"• {get_text('emergency_services', language, default='Швидка допомога')}: 103\n\n"
    
    emergency_text += f"🤖 **{get_text('ai_support', language, default='ШІ підтримка')}:**\n"
    emergency_text += get_text("ai_emergency_help", language,
                             default="Наш ШІ-асистент може надати негайну підтримку та допомогу в кризовій ситуації.")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📞 7333 - " + get_text("call_crisis_line", language, default="Подзвонити на кризову лінію"),
                url="tel:7333"
            )
        ],
        [
            InlineKeyboardButton(
                text="🤖 " + get_text("talk_to_ai_now", language, default="Поговорити з ШІ зараз"),
                callback_data="ai_chat"
            )
        ],
        [
            InlineKeyboardButton(
                text="🫁 " + get_text("breathing_exercise", language, default="Дихальна вправа"),
                callback_data="breathing_exercise"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_psychologist", language, default="Назад до психологів"),
                callback_data="psychologist_online"
            )
        ]
    ])
    
    await callback.message.edit_text(
        emergency_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "group_therapy")
async def group_therapy(callback: CallbackQuery, language: str = "uk"):
    """Show group therapy options"""
    await callback.answer()
    
    group_text = f"👥 **{get_text('group_therapy_title', language, default='Групова терапія')}**\n\n"
    group_text += get_text("group_therapy_intro", language,
                         default="Групова терапія - ефективний спосіб отримати підтримку від людей з подібним досвідом.")
    
    group_text += f"\n\n🎯 **{get_text('available_groups', language, default='Доступні групи')}:**\n\n"
    
    groups = [
        {
            "name": get_text("veterans_support_group", language, default="Група підтримки ветеранів"),
            "schedule": get_text("tuesdays_thursdays", language, default="Вівторок, четвер 18:00"),
            "participants": "8-12"
        },
        {
            "name": get_text("ptsd_group", language, default="Група роботи з ПТСР"),
            "schedule": get_text("mondays_wednesdays", language, default="Понеділок, середа 19:00"),
            "participants": "6-10"
        },
        {
            "name": get_text("family_support_group", language, default="Група для сімей ветеранів"),
            "schedule": get_text("saturdays", language, default="Субота 16:00"),
            "participants": "5-8"
        }
    ]
    
    for i, group in enumerate(groups, 1):
        group_text += f"{i}. **{group['name']}**\n"
        group_text += f"   📅 {get_text('schedule', language, default='Розклад')}: {group['schedule']}\n"
        group_text += f"   👥 {get_text('participants', language, default='Учасників')}: {group['participants']}\n\n"
    
    group_text += f"💡 **{get_text('group_benefits', language, default='Переваги групової терапії')}:**\n"
    group_text += f"• {get_text('peer_support', language, default='Підтримка однолітків')}\n"
    group_text += f"• {get_text('shared_experience', language, default='Спільний досвід')}\n"
    group_text += f"• {get_text('professional_guidance', language, default='Професійне керівництво')}\n"
    group_text += f"• {get_text('confidential_environment', language, default='Конфіденційне середовище')}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("join_group", language, default="Приєднатися до групи"),
                callback_data="join_group"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("group_info", language, default="Детальна інформація"),
                callback_data="group_info"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_psychologist", language, default="Назад до психологів"),
                callback_data="psychologist_online"
            )
        ]
    ])
    
    await callback.message.edit_text(
        group_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "my_sessions")
async def my_sessions(callback: CallbackQuery, language: str = "uk"):
    """Show user's therapy sessions"""
    await callback.answer()
    
    sessions_text = f"📋 **{get_text('my_sessions_title', language, default='Мої сесії')}**\n\n"
    sessions_text += get_text("no_sessions_yet", language,
                            default="У вас поки немає запланованих сесій з психологами.\n\nСкористайтесь функцією пошуку психолога для запису на консультацію.")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("find_psychologist", language, default="Знайти психолога"),
                callback_data="find_psychologist"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("emergency_consultation", language, default="Екстрена консультація"),
                callback_data="emergency_consultation"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_psychologist", language, default="Назад до психологів"),
                callback_data="psychologist_online"
            )
        ]
    ])
    
    await callback.message.edit_text(
        sessions_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )