from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import json

from database.db_manager import db_manager
from utils.keyboards import get_legal_keyboard, get_main_menu_keyboard
from utils.texts import get_text

router = Router()

@router.callback_query(F.data == "my_rights")
async def legal_menu(callback: CallbackQuery, language: str = "uk"):
    """Show legal information menu"""
    await callback.answer()
    
    menu_text = get_text("legal_menu_text", language, 
                        default="📜 Правова інформація для ветеранів\n\nОберіть категорію:")
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=get_legal_keyboard(language)
    )

@router.callback_query(F.data.startswith("legal_"))
async def show_legal_category(callback: CallbackQuery, language: str = "uk"):
    """Show legal documents by category"""
    await callback.answer()
    
    category = callback.data.split("_")[1]  # benefits, compensation, medical, procedures
    
    try:
        # Load legal documents from catalog
        with open("catalog.json", "r", encoding="utf-8") as f:
            catalog = json.load(f)
        
        documents = catalog.get("legal_documents", {}).get(f"veterans_{category}", [])
        
        if not documents:
            await callback.message.edit_text(
                get_text("no_legal_documents", language, default="Документи не знайдено"),
                reply_markup=get_legal_keyboard(language)
            )
            return
        
        # Create documents list
        documents_text = f"📋 **{get_text(f'legal_{category}', language)}**\n\n"
        
        keyboard_buttons = []
        
        for i, doc in enumerate(documents, 1):
            title = doc["title"].get(language, doc["title"]["uk"])
            documents_text += f"{i}. {title}\n"
            
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{i}. {title[:30]}...",
                    callback_data=f"doc_{doc['id']}"
                )
            ])
        
        # Add navigation buttons
        keyboard_buttons.extend([
            [
                InlineKeyboardButton(
                    text=get_text("back_to_legal", language, default="Назад до правової інформації"),
                    callback_data="my_rights"
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
            documents_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("legal_error", language, default="Помилка завантаження правової інформації"),
            reply_markup=get_main_menu_keyboard(language)
        )

@router.callback_query(F.data.startswith("doc_"))
async def show_legal_document(callback: CallbackQuery, language: str = "uk"):
    """Show specific legal document"""
    await callback.answer()
    
    doc_id = callback.data.split("_")[1]
    
    try:
        # Load document from catalog
        with open("catalog.json", "r", encoding="utf-8") as f:
            catalog = json.load(f)
        
        # Find document by ID
        document = None
        for category_docs in catalog.get("legal_documents", {}).values():
            for doc in category_docs:
                if doc["id"] == doc_id:
                    document = doc
                    break
            if document:
                break
        
        if not document:
            await callback.message.edit_text(
                get_text("document_not_found", language, default="Документ не знайдено"),
                reply_markup=get_legal_keyboard(language)
            )
            return
        
        # Format document
        title = document["title"].get(language, document["title"]["uk"])
        content = document["content"].get(language, document["content"]["uk"])
        
        doc_text = f"📄 **{title}**\n\n"
        doc_text += content
        
        # Add metadata
        if document.get("last_updated"):
            doc_text += f"\n\n📅 {get_text('last_updated', language, default='Останнє оновлення')}: {document['last_updated']}"
        
        if document.get("source_url"):
            doc_text += f"\n🔗 {get_text('source', language, default='Джерело')}: {document['source_url']}"
        
        # Create keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("share_document", language, default="Поділитися"),
                    callback_data=f"share_{doc_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back_to_legal", language, default="Назад до правової інформації"),
                    callback_data="my_rights"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back_to_menu", language),
                    callback_data="main_menu"
                )
            ]
        ])
        
        # Split long messages
        if len(doc_text) > 4000:
            # Send in parts
            parts = [doc_text[i:i+4000] for i in range(0, len(doc_text), 4000)]
            
            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # Last part
                    await callback.message.edit_text(
                        part,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
                else:
                    await callback.message.answer(part, parse_mode="Markdown")
        else:
            await callback.message.edit_text(
                doc_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text("document_error", language, default="Помилка завантаження документа"),
            reply_markup=get_legal_keyboard(language)
        )

@router.callback_query(F.data.startswith("share_"))
async def share_document(callback: CallbackQuery, language: str = "uk"):
    """Share legal document"""
    await callback.answer()
    
    doc_id = callback.data.split("_")[1]
    
    share_text = get_text("document_shared", language, 
                         default="📤 Документ готовий до поширення!\n\nВи можете переслати це повідомлення іншим ветеранам.")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("back_to_document", language, default="Назад до документа"),
                callback_data=f"doc_{doc_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_legal", language, default="Назад до правової інформації"),
                callback_data="my_rights"
            )
        ]
    ])
    
    await callback.message.edit_text(
        share_text,
        reply_markup=keyboard
    )

@router.callback_query(F.data == "legal_templates")
async def legal_templates(callback: CallbackQuery, language: str = "uk"):
    """Show legal document templates"""
    await callback.answer()
    
    templates_text = get_text("legal_templates_text", language, 
                             default="📋 Шаблони документів для ветеранів\n\nТут ви можете знайти готові шаблони заяв та документів:")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("disability_application", language, default="Заява на інвалідність"),
                callback_data="template_disability"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("benefits_application", language, default="Заява на пільги"),
                callback_data="template_benefits"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("housing_application", language, default="Заява на житло"),
                callback_data="template_housing"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_legal", language, default="Назад до правової інформації"),
                callback_data="my_rights"
            )
        ]
    ])
    
    await callback.message.edit_text(
        templates_text,
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("template_"))
async def show_template(callback: CallbackQuery, language: str = "uk"):
    """Show document template"""
    await callback.answer()
    
    template_type = callback.data.split("_")[1]
    
    templates = {
        "disability": {
            "title": get_text("disability_template_title", language, default="Заява на встановлення інвалідності"),
            "content": get_text("disability_template_content", language, 
                              default="До медико-соціальної експертної комісії\n\nЗАЯВА\n\nПрошу провести медико-соціальну експертизу для встановлення групи інвалідності у зв'язку з [вказати причину].\n\nДо заяви додаю:\n1. Копію паспорта\n2. Медичні документи\n3. Посвідчення учасника бойових дій\n\nДата: ___________\nПідпис: ___________")
        },
        "benefits": {
            "title": get_text("benefits_template_title", language, default="Заява на отримання пільг"),
            "content": get_text("benefits_template_content", language,
                              default="До управління соціального захисту населення\n\nЗАЯВА\n\nПрошу надати мені пільги, передбачені для ветеранів війни відповідно до чинного законодавства.\n\nДо заяви додаю необхідні документи.\n\nДата: ___________\nПідпис: ___________")
        },
        "housing": {
            "title": get_text("housing_template_title", language, default="Заява на отримання житла"),
            "content": get_text("housing_template_content", language,
                              default="До місцевої державної адміністрації\n\nЗАЯВА\n\nПрошу поставити мене на облік для отримання житла як учасника бойових дій.\n\nДо заяви додаю:\n1. Довідку про склад сім'ї\n2. Посвідчення учасника бойових дій\n3. Довідку про доходи\n\nДата: ___________\nПідпис: ___________")
        }
    }
    
    template = templates.get(template_type)
    
    if not template:
        await callback.message.edit_text(
            get_text("template_not_found", language, default="Шаблон не знайдено"),
            reply_markup=get_legal_keyboard(language)
        )
        return
    
    template_text = f"📄 **{template['title']}**\n\n```\n{template['content']}\n```"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("copy_template", language, default="Копіювати шаблон"),
                callback_data=f"copy_{template_type}"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("back_to_templates", language, default="Назад до шаблонів"),
                callback_data="legal_templates"
            )
        ]
    ])
    
    await callback.message.edit_text(
        template_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )