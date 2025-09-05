from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import json
from datetime import datetime, timedelta

from database.db_manager import db_manager
from database.models import TelemedicineAppointment
from utils.keyboards import get_telemedicine_keyboard, get_main_menu_keyboard
from utils.texts import get_text

router = Router()

@router.callback_query(F.data == "telemedicine")
async def telemedicine_menu(callback: CallbackQuery, language: str = "uk"):
    """Show telemedicine menu"""
    await callback.answer()
    
    menu_text = get_text("telemedicine_menu_text", language,
                        default="🏥 Телемедичні послуги\n\nОберіть дію:")
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=get_telemedicine_keyboard(language)
    )

@router.callback_query(F.data == "book_appointment")
async def book_appointment_menu(callback: CallbackQuery, language: str = "uk"):
    """Show appointment booking options"""
    await callback.answer()
    
    try:
        # Load telemedicine providers from catalog
        with open("catalog.json", "r", encoding="utf-8") as f:
            catalog = json.load(f)
        
        providers = catalog.get("telemedicine_providers", [])
        
        if not providers:
            await callback.message.edit_text(
                get_text("no_providers", language, default="Провайдери не знайдені"),
                reply_markup=get_telemedicine_keyboard(language)
            )
            return
        
        booking_text = f"📅 **{get_text('book_appointment_title', language, default='Записатися на прийом')}**\n\n"
        booking_text += get_text("select_provider", language, default="Оберіть провайдера телемедицини:")
        
        keyboard_buttons = []
        
        for provider in providers:
            name = provider["name"]
            specializations = ", ".join(provider.get("specializations", []))
            
            button_text = f"🏥 {name}"
            if specializations:
                button_text += f" ({specializations})"
            
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"provider_{name.lower().replace(' ', '_')}"
                )
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=get_text("back_to_telemedicine", language, default="Назад до телемедицини"),
                callback_data="telemedicine"
            )
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            booking_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("booking_error", language, default="Помилка завантаження провайдерів"),
            reply_markup=get_telemedicine_keyboard(language)
        )

@router.callback_query(F.data.startswith("provider_"))
async def show_provider_info(callback: CallbackQuery, language: str = "uk"):
    """Show provider information and booking options"""
    await callback.answer()
    
    provider_id = callback.data.split("_", 1)[1]
    
    try:
        # Load provider info
        with open("catalog.json", "r", encoding="utf-8") as f:
            catalog = json.load(f)
        
        providers = catalog.get("telemedicine_providers", [])
        provider = None
        
        for p in providers:
            if p["name"].lower().replace(" ", "_") == provider_id:
                provider = p
                break
        
        if not provider:
            await callback.message.edit_text(
                get_text("provider_not_found", language, default="Провайдер не знайдений"),
                reply_markup=get_telemedicine_keyboard(language)
            )
            return
        
        # Format provider info
        provider_text = f"🏥 **{provider['name']}**\n\n"
        
        if provider.get("specializations"):
            specializations = provider["specializations"]
            spec_text = get_text("specializations", language, default="Спеціалізації")
            provider_text += f"👨‍⚕️ **{spec_text}:** {', '.join(specializations)}\n\n"
        
        if provider.get("languages"):
            languages = provider["languages"]
            lang_text = get_text("languages", language, default="Мови")
            provider_text += f"🗣 **{lang_text}:** {', '.join(languages)}\n\n"
        
        if provider.get("features"):
            features = provider["features"]
            features_text = get_text("features", language, default="Можливості")
            provider_text += f"⚡ **{features_text}:** {', '.join(features)}\n\n"
        
        provider_text += get_text("booking_notice", language,
                                default="📝 Для запису на консультацію натисніть кнопку нижче. Ви будете перенаправлені на сайт провайдера.")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🌐 {get_text('visit_website', language, default='Перейти на сайт')} {provider['name']}",
                    url=provider.get("url", "#")
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("book_with_provider", language, default="Записатися"),
                    callback_data=f"book_{provider_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back_to_providers", language, default="Назад до провайдерів"),
                    callback_data="book_appointment"
                )
            ]
        ])
        
        await callback.message.edit_text(
            provider_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("provider_error", language, default="Помилка завантаження інформації про провайдера"),
            reply_markup=get_telemedicine_keyboard(language)
        )

@router.callback_query(F.data.startswith("book_"))
async def book_with_provider(callback: CallbackQuery, language: str = "uk"):
    """Book appointment with specific provider"""
    await callback.answer()
    
    provider_id = callback.data.split("_", 1)[1]
    user_id = callback.from_user.id
    
    # For now, we'll create a placeholder appointment and direct to external booking
    try:
        # Create appointment record
        appointment = TelemedicineAppointment(
            user_id=user_id,
            doctor_name="TBD",
            specialization="psychology"
        )
        appointment.status = "pending_external"
        
        # In a real implementation, you would integrate with the provider's API
        booking_text = f"📅 **{get_text('booking_initiated', language, default='Запис ініційовано')}**\n\n"
        booking_text += get_text("booking_instructions", language,
                                default="Для завершення запису:\n\n1. Перейдіть на сайт провайдера\n2. Оберіть спеціаліста\n3. Виберіть зручний час\n4. Підтвердіть запис\n\nПісля підтвердження ви отримаєте деталі консультації.")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("continue_booking", language, default="Продовжити запис"),
                    url="https://helsi.me/"  # Default to Helsi
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("my_appointments", language, default="Мої записи"),
                    callback_data="my_appointments"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back_to_telemedicine", language, default="Назад до телемедицини"),
                    callback_data="telemedicine"
                )
            ]
        ])
        
        await callback.message.edit_text(
            booking_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("booking_failed", language, default="Помилка створення запису"),
            reply_markup=get_telemedicine_keyboard(language)
        )

@router.callback_query(F.data == "my_appointments")
async def show_my_appointments(callback: CallbackQuery, language: str = "uk"):
    """Show user's appointments"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    try:
        # Get user appointments from database
        async with db_manager.pool.acquire() as conn:
            appointments = await conn.fetch('''
                SELECT * FROM telemedicine_appointments 
                WHERE user_id = $1 
                ORDER BY appointment_date DESC, appointment_time DESC
                LIMIT 10
            ''', user_id)
        
        if not appointments:
            appointments_text = get_text("no_appointments", language,
                                       default="📅 У вас поки немає записів на консультації.\n\nСкористайтесь функцією 'Записатися на прийом' для створення нового запису.")
        else:
            appointments_text = f"📅 **{get_text('my_appointments_title', language, default='Мої записи')}**\n\n"
            
            for i, apt in enumerate(appointments, 1):
                status_emoji = {
                    "pending": "⏳",
                    "confirmed": "✅", 
                    "completed": "✅",
                    "cancelled": "❌"
                }.get(apt["status"], "📅")
                
                appointments_text += f"{status_emoji} **{get_text('appointment', language, default='Запис')} #{i}**\n"
                appointments_text += f"👨‍⚕️ {apt['doctor_name']}\n"
                appointments_text += f"🏥 {apt['specialization']}\n"
                
                if apt["appointment_date"]:
                    appointments_text += f"📅 {apt['appointment_date'].strftime('%d.%m.%Y')}\n"
                if apt["appointment_time"]:
                    appointments_text += f"🕐 {apt['appointment_time'].strftime('%H:%M')}\n"
                
                status_text = get_text(f"status_{apt['status']}", language, default=apt["status"])
                appointments_text += f"📊 {get_text('status', language, default='Статус')}: {status_text}\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("book_new_appointment", language, default="Новий запис"),
                    callback_data="book_appointment"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back_to_telemedicine", language, default="Назад до телемедицини"),
                    callback_data="telemedicine"
                )
            ]
        ])
        
        await callback.message.edit_text(
            appointments_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("appointments_error", language, default="Помилка завантаження записів"),
            reply_markup=get_telemedicine_keyboard(language)
        )

@router.callback_query(F.data == "find_specialist")
async def find_specialist(callback: CallbackQuery, language: str = "uk"):
    """Help find appropriate specialist"""
    await callback.answer()
    
    specialist_text = f"🔍 **{get_text('find_specialist_title', language, default='Пошук спеціаліста')}**\n\n"
    specialist_text += get_text("specialist_guide", language,
                              default="Оберіть тип спеціаліста залежно від ваших потреб:")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🧠 " + get_text("psychologist", language, default="Психолог"),
                callback_data="specialist_psychologist"
            )
        ],
        [
            InlineKeyboardButton(
                text="👨‍⚕️ " + get_text("psychiatrist", language, default="Психіатр"),
                callback_data="specialist_psychiatrist"
            )
        ],
        [
            InlineKeyboardButton(
                text="🩺 " + get_text("general_practitioner", language, default="Сімейний лікар"),
                callback_data="specialist_general"
            )
        ],
        [
            InlineKeyboardButton(
                text="🫀 " + get_text("trauma_specialist", language, default="Спеціаліст з травм"),
                callback_data="specialist_trauma"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_telemedicine", language, default="Назад до телемедицини"),
                callback_data="telemedicine"
            )
        ]
    ])
    
    await callback.message.edit_text(
        specialist_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("specialist_"))
async def show_specialist_info(callback: CallbackQuery, language: str = "uk"):
    """Show information about specialist type"""
    await callback.answer()
    
    specialist_type = callback.data.split("_")[1]
    
    specialist_info = {
        "psychologist": {
            "title": get_text("psychologist_title", language, default="🧠 Психолог"),
            "description": get_text("psychologist_desc", language,
                                  default="Психолог допомагає з емоційними проблемами, стресом, тривогою та депресією. Підходить для:\n\n• Розмов про почуття\n• Подолання стресу\n• Робота з травмами\n• Покращення настрою"),
            "when_needed": get_text("psychologist_when", language,
                                  default="Звертайтесь, якщо відчуваєте тривогу, депресію, стрес або потребуєте емоційної підтримки.")
        },
        "psychiatrist": {
            "title": get_text("psychiatrist_title", language, default="👨‍⚕️ Психіатр"),
            "description": get_text("psychiatrist_desc", language,
                                  default="Психіатр - лікар, який може призначати ліки та лікувати серйозні психічні розлади. Підходить для:\n\n• Призначення медикаментів\n• Лікування депресії\n• Біполярний розлад\n• ПТСР"),
            "when_needed": get_text("psychiatrist_when", language,
                                  default="Звертайтесь при серйозних симптомах, потребі в медикаментах або діагностиці.")
        },
        "general": {
            "title": get_text("general_title", language, default="🩺 Сімейний лікар"),
            "description": get_text("general_desc", language,
                                  default="Сімейний лікар надає загальну медичну допомогу та може направити до спеціалістів. Підходить для:\n\n• Загальних проблем зі здоров'ям\n• Первинної консультації\n• Направлень до спеціалістів\n• Профілактики"),
            "when_needed": get_text("general_when", language,
                                  default="Звертайтесь для загальної оцінки здоров'я та первинної консультації.")
        },
        "trauma": {
            "title": get_text("trauma_title", language, default="🫀 Спеціаліст з травм"),
            "description": get_text("trauma_desc", language,
                                  default="Спеціаліст з травм працює з ПТСР та наслідками травматичних подій. Підходить для:\n\n• ПТСР\n• Військові травми\n• Флешбеки та кошмари\n• Емоційне оніміння"),
            "when_needed": get_text("trauma_when", language,
                                  default="Звертайтесь при симптомах ПТСР, флешбеках, кошмарах або після травматичних подій.")
        }
    }
    
    info = specialist_info.get(specialist_type)
    
    if not info:
        await callback.message.edit_text(
            get_text("specialist_not_found", language, default="Інформація не знайдена"),
            reply_markup=get_telemedicine_keyboard(language)
        )
        return
    
    info_text = f"{info['title']}\n\n"
    info_text += f"📝 **{get_text('description', language, default='Опис')}:**\n{info['description']}\n\n"
    info_text += f"⚡ **{get_text('when_to_contact', language, default='Коли звертатись')}:**\n{info['when_needed']}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("book_with_specialist", language, default="Записатися до цього спеціаліста"),
                callback_data="book_appointment"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_specialists", language, default="Назад до спеціалістів"),
                callback_data="find_specialist"
            )
        ]
    ])
    
    await callback.message.edit_text(
        info_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )