from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import json

from utils.keyboards import get_hotlines_keyboard, get_main_menu_keyboard
from utils.texts import get_text

router = Router()

@router.callback_query(F.data == "hotlines")
async def hotlines_menu(callback: CallbackQuery, language: str = "uk"):
    """Show hotlines menu"""
    await callback.answer()
    
    menu_text = get_text("hotlines_menu_text", language,
                        default="📞 Гарячі лінії підтримки\n\nОберіть тип допомоги:")
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=get_hotlines_keyboard(language)
    )

@router.callback_query(F.data.startswith("hotline_"))
async def show_hotlines(callback: CallbackQuery, language: str = "uk"):
    """Show specific category hotlines"""
    await callback.answer()
    
    category = callback.data.split("_")[1]  # crisis, mental, veterans, legal, medical
    
    try:
        # Load hotlines from catalog
        with open("catalog.json", "r", encoding="utf-8") as f:
            catalog = json.load(f)
        
        # Map categories to catalog keys
        category_map = {
            "crisis": "crisis_support",
            "mental": "crisis_support", 
            "veterans": "veterans_support",
            "legal": "veterans_support",
            "medical": "medical_emergency"
        }
        
        catalog_key = category_map.get(category, "crisis_support")
        hotlines = catalog.get("hotlines", {}).get(catalog_key, [])
        
        if not hotlines:
            await callback.message.edit_text(
                get_text("no_hotlines", language, default="Гарячі лінії не знайдено"),
                reply_markup=get_hotlines_keyboard(language)
            )
            return
        
        # Format hotlines text
        category_titles = {
            "crisis": get_text("crisis_hotlines", language, default="🆘 Кризові гарячі лінії"),
            "mental": get_text("mental_health_hotlines", language, default="🧠 Психологічна підтримка"),
            "veterans": get_text("veterans_hotlines", language, default="🎖️ Підтримка ветеранів"),
            "legal": get_text("legal_hotlines", language, default="⚖️ Правова підтримка"),
            "medical": get_text("medical_hotlines", language, default="🏥 Медична допомога")
        }
        
        hotlines_text = f"**{category_titles.get(category, 'Гарячі лінії')}**\n\n"
        
        for hotline in hotlines:
            name = hotline["name"].get(language, hotline["name"]["uk"])
            phone = hotline["phone"]
            description = hotline["description"].get(language, hotline["description"]["uk"])
            availability = hotline.get("availability", "24/7")
            
            hotlines_text += f"📞 **{name}**\n"
            hotlines_text += f"☎️ {phone}\n"
            hotlines_text += f"📝 {description}\n"
            hotlines_text += f"🕐 {availability}\n\n"
        
        # Add emergency notice for crisis hotlines
        if category == "crisis":
            hotlines_text += f"⚠️ **{get_text('emergency_notice', language, default='УВАГА')}**\n"
            hotlines_text += get_text("crisis_emergency_text", language,
                                    default="Якщо ви перебуваете в небезпеці або маєте думки про самогубство, негайно зверніться за допомогою!")
        
        # Create keyboard
        keyboard_buttons = []
        
        # Add quick dial buttons for main numbers
        if category == "crisis":
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text="📞 7333 - " + get_text("call_now", language, default="Подзвонити зараз"),
                    url="tel:7333"
                )
            ])
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text="📞 116 123 - " + get_text("call_now", language, default="Подзвонити зараз"),
                    url="tel:116123"
                )
            ])
        
        # Navigation buttons
        keyboard_buttons.extend([
            [
                InlineKeyboardButton(
                    text=get_text("back_to_hotlines", language, default="Назад до гарячих ліній"),
                    callback_data="hotlines"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back_to_menu", language),
                    callback_data="main_menu"
                )
            ]
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            hotlines_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("hotlines_error", language, default="Помилка завантаження гарячих ліній"),
            reply_markup=get_main_menu_keyboard(language)
        )

@router.callback_query(F.data == "crisis_hotline")
async def crisis_hotline_direct(callback: CallbackQuery, language: str = "uk"):
    """Direct access to crisis hotlines"""
    await callback.answer()
    
    crisis_text = f"🆘 **{get_text('crisis_support_title', language, default='Кризова підтримка')}**\n\n"
    
    crisis_text += f"📞 **{get_text('national_suicide_prevention', language, default='Національна лінія попередження самогубств')}**\n"
    crisis_text += f"☎️ 7333 (безкоштовно, цілодобово)\n\n"
    
    crisis_text += f"📞 **{get_text('psychological_support_line', language, default='Лінія психологічної підтримки')}**\n"
    crisis_text += f"☎️ 116 123 (цілодобово)\n\n"
    
    crisis_text += f"📞 **{get_text('emergency_services', language, default='Швидка допомога')}**\n"
    crisis_text += f"☎️ 103\n\n"
    
    remember_text = get_text('remember', language, default="Пам'ятайте")
    crisis_text += f"❤️ **{remember_text}:**\n"
    crisis_text += get_text("crisis_remember_text", language,
                           default="• Ви не самі\n• Ваше життя має цінність\n• Допомога завжди доступна\n• Кризи минають")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📞 7333 - " + get_text("call_crisis_line", language, default="Подзвонити на кризову лінію"),
                url="tel:7333"
            )
        ],
        [
            InlineKeyboardButton(
                text="📞 116 123 - " + get_text("call_support_line", language, default="Психологічна підтримка"),
                url="tel:116123"
            )
        ],
        [
            InlineKeyboardButton(
                text="🤖 " + get_text("talk_to_ai", language, default="Поговорити з ШІ"),
                callback_data="ai_chat"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_hotlines", language, default="Назад до гарячих ліній"),
                callback_data="hotlines"
            )
        ]
    ])
    
    await callback.message.edit_text(
        crisis_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
