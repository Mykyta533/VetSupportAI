from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db_manager import db_manager
from database.models import User, UserRole
from utils.keyboards import get_main_menu_keyboard
from utils.texts import get_text

router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_consent = State()
    waiting_for_veteran_status = State()
    waiting_for_contact_info = State()

@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext, language: str = "uk"):
    """Handle /start command"""
    user_id = message.from_user.id
    existing_user = await db_manager.get_user(user_id)
    
    if existing_user and existing_user.terms_accepted and existing_user.privacy_accepted:
        # Existing user - show main menu
        await message.answer(
            get_text("welcome_back", language).format(
                name=existing_user.first_name or message.from_user.first_name
            ),
            reply_markup=get_main_menu_keyboard(language)
        )
        return
    
    # New user or incomplete registration
    welcome_text = get_text("welcome_new_user", language)
    
    consent_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("accept_terms", language),
                callback_data="accept_terms"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("read_terms", language),
                callback_data="read_terms"
            )
        ]
    ])
    
    await message.answer(welcome_text, reply_markup=consent_keyboard)
    await state.set_state(RegistrationStates.waiting_for_consent)

@router.callback_query(F.data == "accept_terms")
async def accept_terms_callback(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Handle terms acceptance"""
    await callback.answer()
    
    veteran_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("yes_veteran", language),
                callback_data="veteran_yes"
            ),
            InlineKeyboardButton(
                text=get_text("no_veteran", language),
                callback_data="veteran_no"
            )
        ]
    ])
    
    await callback.message.edit_text(
        get_text("veteran_question", language),
        reply_markup=veteran_keyboard
    )
    
    await state.set_state(RegistrationStates.waiting_for_veteran_status)

@router.callback_query(F.data.in_(["veteran_yes", "veteran_no"]))
async def veteran_status_callback(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Handle veteran status selection"""
    await callback.answer()
    
    is_veteran = callback.data == "veteran_yes"
    await state.update_data(is_veteran=is_veteran)
    
    # Create user account
    user = User(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
        language=language,
        role=UserRole.USER
    )
    user.is_veteran = is_veteran
    user.terms_accepted = True
    user.privacy_accepted = True
    
    success = await db_manager.create_user(user)
    
    if success:
        welcome_message = get_text("registration_complete", language)
        if is_veteran:
            welcome_message += "\n\n" + get_text("veteran_benefits", language)
        
        await callback.message.edit_text(
            welcome_message,
            reply_markup=get_main_menu_keyboard(language)
        )
    else:
        await callback.message.edit_text(
            get_text("registration_error", language)
        )
    
    await state.clear()

@router.callback_query(F.data == "read_terms")
async def read_terms_callback(callback: CallbackQuery, language: str = "uk"):
    """Show terms and conditions"""
    await callback.answer()
    
    terms_text = get_text("terms_and_conditions", language)
    
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("back_to_registration", language),
                callback_data="back_to_start"
            )
        ]
    ])
    
    await callback.message.edit_text(terms_text, reply_markup=back_keyboard)

@router.callback_query(F.data == "back_to_start")
async def back_to_start_callback(callback: CallbackQuery, state: FSMContext, language: str = "uk"):
    """Return to start registration"""
    await callback.answer()
    await start_command(callback.message, state, language)

@router.message(Command("help"))
async def help_command(message: Message, language: str = "uk"):
    """Handle /help command"""
    help_text = get_text("help_text", language)
    await message.answer(help_text, reply_markup=get_main_menu_keyboard(language))

@router.message(Command("menu"))
async def menu_command(message: Message, language: str = "uk"):
    """Handle /menu command"""
    await message.answer(
        get_text("main_menu", language),
        reply_markup=get_main_menu_keyboard(language)
    )

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, language: str = "uk"):
    """Handle main menu callback"""
    await callback.answer()
    await callback.message.edit_text(
        get_text("main_menu", language),
        reply_markup=get_main_menu_keyboard(language)
    )